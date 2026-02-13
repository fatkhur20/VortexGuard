import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ChatMemberHandler,
    CallbackQueryHandler,
)

from src.config import TELEGRAM_BOT_TOKEN, RULES_TEXT, SLOW_MODE_DURATION, MUTE_DURATION_MINUTES, TRUST_MSG_THRESHOLD, VERIFICATION_TIMEOUT
from src.moderation import auto_moderator
from src.antiraid import anti_raid
from src.lifecycle import member_lifecycle
from src.logger import logger
from src.storage import storage
from src.admin import lock_chat, unlock_chat, purge_messages

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am GuardianAI, the group manager. I am active.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RULES_TEXT)

async def lift_raid_lock(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    anti_raid.reset()
    await context.bot.set_chat_permissions(
        chat_id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_invite_users=True
        )
    )
    await context.bot.send_message(chat_id, "✅ Raid protection lifted. Chat unlocked.")

async def kick_unverified(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.user_id
    chat_id = context.job.chat_id

    if member_lifecycle.is_pending(user_id):
        await context.bot.send_message(chat_id, f"👢 User {user_id} kicked for failing to verify.")
        await context.bot.ban_chat_member(chat_id, user_id)
        await context.bot.unban_chat_member(chat_id, user_id)

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles new members joining.
    """
    result = update.chat_member
    new_member = result.new_chat_member

    if new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED] and \
       result.old_chat_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:

        user = new_member.user
        chat_id = update.effective_chat.id

        logger.info(f"New member joined: {user.id} ({user.first_name})")

        # Anti-Raid Check
        if anti_raid.register_join():
            logger.warning("Raid detected! Enabling slow mode.")
            await context.bot.send_message(chat_id, f"⚠️ High join rate detected. Slow mode enabled ({SLOW_MODE_DURATION}s).")

            await context.bot.set_chat_permissions(
                chat_id,
                ChatPermissions(can_send_messages=False)
            )
            await context.bot.send_message(chat_id, "🔒 Chat temporarily locked due to raid.")

            # Schedule unlock
            context.job_queue.run_once(lift_raid_lock, SLOW_MODE_DURATION, chat_id=chat_id)

        # Lifecycle Management
        member_lifecycle.add_new_member(user.id)

        # Restrict the user immediately
        permissions = ChatPermissions(can_send_messages=False)
        await context.bot.restrict_chat_member(chat_id, user.id, permissions=permissions)

        # Send Verification Captcha
        keyboard = [
            [InlineKeyboardButton("I am human", callback_data=f"verify_{user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id,
            f"Welcome {user.mention_html()}! Please verify to speak within {VERIFICATION_TIMEOUT}s.",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

        # Schedule Kick
        context.job_queue.run_once(kick_unverified, VERIFICATION_TIMEOUT, user_id=user.id, chat_id=chat_id)

async def handle_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles button clicks for verification.
    """
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("verify_"):
        target_id = int(data.split("_")[1])
        user_id = query.from_user.id

        if user_id != target_id:
            await query.answer("This verification is not for you!", show_alert=True)
            return

        member_lifecycle.verify_member(user_id)

        # Lift restrictions
        chat_id = update.effective_chat.id
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_invite_users=True
        )
        await context.bot.restrict_chat_member(chat_id, user_id, permissions=permissions)

        await query.edit_message_text(f"✅ User {query.from_user.first_name} verified.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Monitors messages for violations.
    """
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    text = update.message.text
    chat_id = update.effective_chat.id

    # Check Verification
    if not member_lifecycle.is_verified(user.id):
        # In case restriction failed or expired, re-restrict or warn?
        pass

    # Trust System Update
    msg_count = storage.increment_msg_count(user.id)

    # Check Trust for Links/Media
    # If user has sent fewer than threshold messages, block links (simple check)
    if msg_count < TRUST_MSG_THRESHOLD:
        if "http" in text or "www." in text or "@" in text:
            await update.message.delete()
            await context.bot.send_message(chat_id, f"⚠️ {user.mention_html()}: You need {TRUST_MSG_THRESHOLD} messages to post links.", parse_mode="HTML")
            return

    # Flood Control
    if auto_moderator.check_flood(user.id):
        await update.message.delete()
        await context.bot.send_message(chat_id, f"⚠️ {user.mention_html()}: Slow down!", parse_mode="HTML")
        return

    # Heated Debate De-escalation
    if auto_moderator.detect_heated_debate(text):
        await context.bot.send_message(chat_id, f"⚠️ Discussion is getting heated. Let's keep it cool, {user.first_name}.", parse_mode="HTML")

    # FAQ
    faq_answer = auto_moderator.check_faq(text)
    if faq_answer:
         await update.message.reply_text(f"🤖 {faq_answer}")
         return

    # Auto Moderation
    is_violation, reason = auto_moderator.check_content(text)
    if is_violation:
        # Delete the message
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")

        # Register violation and get action
        action = auto_moderator.register_violation(user.id)
        logger.info(f"Violation by {user.id}: {reason}. Action: {action}")

        # Execute Action
        if action == "WARNING":
            await context.bot.send_message(chat_id, f"⚠️ Warning for {user.mention_html()}: {reason}. Please follow the rules.", parse_mode="HTML")

        elif action == "MUTE":
            await context.bot.send_message(chat_id, f"🔇 Muting {user.mention_html()} for {MUTE_DURATION_MINUTES} minutes due to repeated violations.", parse_mode="HTML")
            permissions = ChatPermissions(can_send_messages=False)
            until = datetime.now() + timedelta(minutes=MUTE_DURATION_MINUTES)
            await context.bot.restrict_chat_member(chat_id, user.id, permissions=permissions, until_date=until)

        elif action == "KICK":
             await context.bot.send_message(chat_id, f"👢 Kicking {user.mention_html()} for repeated violations.", parse_mode="HTML")
             await context.bot.ban_chat_member(chat_id, user.id)
             await context.bot.unban_chat_member(chat_id, user.id) # Unban effectively acts as kick

        elif action == "BAN":
             await context.bot.send_message(chat_id, f"🚫 Banning {user.mention_html()} permanently.", parse_mode="HTML")
             await context.bot.ban_chat_member(chat_id, user.id)

def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("No token found! Set TELEGRAM_BOT_TOKEN in .env")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lock", lock_chat))
    application.add_handler(CommandHandler("unlock", unlock_chat))
    application.add_handler(CommandHandler("purge", purge_messages))
    application.add_handler(CallbackQueryHandler(handle_verification))

    # Note: ChatMemberHandler triggers on status updates
    application.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))

    # Message Handler
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
