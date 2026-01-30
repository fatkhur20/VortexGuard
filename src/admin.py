from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus
from functools import wraps
from .logger import logger

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat

        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await update.message.reply_text("⛔ This command is for admins only.")
            return

        return await func(update, context, *args, **kwargs)
    return wrapper

@admin_only
async def lock_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await context.bot.set_chat_permissions(
        chat.id,
        ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text("🔒 Chat locked by admin.")

@admin_only
async def unlock_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await context.bot.set_chat_permissions(
        chat.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_invite_users=True
        )
    )
    await update.message.reply_text("🔓 Chat unlocked by admin.")

@admin_only
async def purge_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Purges the message replied to, or the last message if no reply.
    (Bulk delete requires more complex logic/permissions)
    """
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
            await update.message.delete() # delete command itself
            await context.bot.send_message(update.effective_chat.id, "🗑️ Message purged.")
        except Exception as e:
            await update.message.reply_text(f"Failed to purge: {e}")
    else:
        await update.message.reply_text("Reply to a message to purge it.")
