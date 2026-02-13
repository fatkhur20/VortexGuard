from .config import FORBIDDEN_KEYWORDS, FLOOD_WINDOW, FLOOD_MAX_MESSAGES, HEATED_KEYWORDS, FAQ_DATA
from .logger import logger
from .storage import storage
import time

class AutoModerator:
    def __init__(self):
        self.message_timestamps = {} # user_id -> [timestamps]

    def check_flood(self, user_id):
        """
        Checks if user is sending too many messages.
        """
        now = time.time()
        timestamps = self.message_timestamps.get(user_id, [])
        # Filter old
        timestamps = [t for t in timestamps if now - t < FLOOD_WINDOW]
        timestamps.append(now)
        self.message_timestamps[user_id] = timestamps

        if len(timestamps) > FLOOD_MAX_MESSAGES:
            return True
        return False

    def detect_heated_debate(self, text):
        """
        Simple heuristic: Check for aggressive keywords.
        """
        if not text:
            return False

        lower = text.lower()
        for kw in HEATED_KEYWORDS:
            if kw in lower:
                return True
        return False

    def check_faq(self, text):
        """
        Returns answer if text matches FAQ keywords.
        """
        if not text: return None
        lower = text.lower()
        for key, answer in FAQ_DATA.items():
            if key in lower:
                return answer
        return None

    def check_content(self, text):
        """
        Checks text for forbidden content.
        Returns (is_violation, reason)
        """
        if not text:
            return False, None

        lower_text = text.lower()
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in lower_text:
                return True, f"Forbidden keyword: {keyword}"

        # Here we could add regex for links, etc.
        return False, None

    def register_violation(self, user_id):
        """
        Registers a violation and returns the action to be taken.
        Escalation:
        1. Warning
        2. Mute
        3. Kick
        4. Ban
        """
        count = storage.add_violation(user_id)

        if count == 1:
            return "WARNING"
        elif count == 2:
            return "MUTE"
        elif count == 3:
            return "KICK"
        else:
            return "BAN"

    def get_violation_count(self, user_id):
        return storage.get_user(user_id)["violations"]

auto_moderator = AutoModerator()
