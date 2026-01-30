import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# General Settings
BOT_NAME = "GuardianAI"

# Auto Moderation Rules
MAX_WARNINGS = 3  # Before mute
MUTE_DURATION_MINUTES = 60
RAID_TRIGGER_COUNT = 5  # Number of joins
RAID_TRIGGER_WINDOW = 10  # Seconds
SLOW_MODE_DURATION = 300  # 5 minutes

# Forbidden Keywords (Simple list for demo purposes)
# In a real system, this might be regex or AI-based.
FORBIDDEN_KEYWORDS = [
    "scam", "free money", "click here", "winner", "prize",
    "badword1", "badword2" # Placeholders
]

# Rules Text
RULES_TEXT = """
1. Be firm, neutral, and calm.
2. No spam, scams, or toxicity.
3. No hate speech or harassment.
4. No NSFW content.
"""

# Lifecycle
VERIFICATION_TIMEOUT = 60 # Seconds to solve captcha
# Flood Control
FLOOD_WINDOW = 5 # Seconds
FLOOD_MAX_MESSAGES = 4 # Max messages in window

# Heated Debate Detection
HEATED_KEYWORDS = [
    "shut up", "idiot", "stupid", "fuck", "bitch", "retard", "dumb",
    "clown", "garbage", "trash"
]
# Trust System
TRUST_MSG_THRESHOLD = 5 # Messages needed to post links/media
# FAQ
FAQ_DATA = {
    "price": "Please check our website for pricing.",
    "rules": "Read the pinned message for rules.",
    "support": "Contact @admin for support.",
    "token": "The token address is 0x123..."
}
