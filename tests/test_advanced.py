import unittest
import time
from src.moderation import AutoModerator
from src.config import FLOOD_MAX_MESSAGES

class TestAdvancedModeration(unittest.TestCase):
    def test_flood_detection(self):
        mod = AutoModerator()
        user_id = 777

        # Send safe amount
        for _ in range(FLOOD_MAX_MESSAGES):
            self.assertFalse(mod.check_flood(user_id))

        # One more triggers flood
        self.assertTrue(mod.check_flood(user_id))

    def test_heated_debate(self):
        mod = AutoModerator()
        self.assertTrue(mod.detect_heated_debate("You are an idiot"))
        self.assertFalse(mod.detect_heated_debate("You are amazing"))

if __name__ == '__main__':
    unittest.main()
