import unittest
import time
from src.moderation import AutoModerator
from src.antiraid import AntiRaid
from src.config import RAID_TRIGGER_COUNT

class TestLogic(unittest.TestCase):
    def test_moderation_escalation(self):
        mod = AutoModerator()
        user_id = 123

        # 1. Warning
        action = mod.register_violation(user_id)
        self.assertEqual(action, "WARNING")

        # 2. Mute
        action = mod.register_violation(user_id)
        self.assertEqual(action, "MUTE")

        # 3. Kick
        action = mod.register_violation(user_id)
        self.assertEqual(action, "KICK")

        # 4. Ban
        action = mod.register_violation(user_id)
        self.assertEqual(action, "BAN")

    def test_forbidden_keywords(self):
        mod = AutoModerator()
        # Assume 'scam' is in FORBIDDEN_KEYWORDS defined in config
        violation, reason = mod.check_content("This is a scam link")
        self.assertTrue(violation)
        if reason:
            self.assertIn("scam", reason)

        violation, reason = mod.check_content("Hello world")
        self.assertFalse(violation)

    def test_antiraid(self):
        raid = AntiRaid()
        # RAID_TRIGGER_COUNT is usually 5 in config

        for _ in range(RAID_TRIGGER_COUNT - 1):
            is_raid = raid.register_join()
            self.assertFalse(is_raid)

        # The Nth join triggers it
        is_raid = raid.register_join()
        self.assertTrue(is_raid)

if __name__ == '__main__':
    unittest.main()
