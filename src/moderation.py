from .config import FORBIDDEN_KEYWORDS
from .logger import logger

class AutoModerator:
    def __init__(self):
        self.user_violations = {} # user_id -> count

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
        count = self.user_violations.get(user_id, 0) + 1
        self.user_violations[user_id] = count

        if count == 1:
            return "WARNING"
        elif count == 2:
            return "MUTE"
        elif count == 3:
            return "KICK"
        else:
            return "BAN"

    def get_violation_count(self, user_id):
        return self.user_violations.get(user_id, 0)

auto_moderator = AutoModerator()
