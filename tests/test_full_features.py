import unittest
import shutil
import os
from src.storage import Storage
from src.moderation import AutoModerator

class TestFullFeatures(unittest.TestCase):
    def setUp(self):
        if os.path.exists("data"):
            shutil.rmtree("data")
        self.storage = Storage()
        self.mod = AutoModerator()

    def tearDown(self):
        if os.path.exists("data"):
            shutil.rmtree("data")

    def test_trust_system_logic(self):
        user_id = 555
        # Simulating message sending
        count = self.storage.increment_msg_count(user_id)
        self.assertEqual(count, 1)

        # Check against threshold logic manually (since main.py requires async/bot mock)
        threshold = 5
        self.assertTrue(count < threshold) # Should block links

        for _ in range(5):
             count = self.storage.increment_msg_count(user_id)

        self.assertTrue(count >= threshold) # Should allow links

    def test_flood_logic_with_storage(self):
        # Flood logic is in-memory in AutoModerator, but let's verify it coexists with storage calls
        user_id = 444
        self.storage.increment_msg_count(user_id)
        is_flood = self.mod.check_flood(user_id)
        self.assertFalse(is_flood)

if __name__ == '__main__':
    unittest.main()
