import unittest
import os
import shutil
from src.storage import Storage

class TestStorage(unittest.TestCase):
    def setUp(self):
        # Clean up before test
        if os.path.exists("data"):
            shutil.rmtree("data")
        self.storage = Storage()

    def tearDown(self):
        # Clean up after test
        if os.path.exists("data"):
            shutil.rmtree("data")

    def test_persistence(self):
        user_id = 999
        self.storage.add_violation(user_id)
        self.assertEqual(self.storage.get_user(user_id)["violations"], 1)

        # Reload
        new_storage = Storage()
        self.assertEqual(new_storage.get_user(user_id)["violations"], 1)

    def test_update_user(self):
        user_id = 888
        self.storage.update_user(user_id, msg_count=50)

        new_storage = Storage()
        self.assertEqual(new_storage.get_user(user_id)["msg_count"], 50)

if __name__ == '__main__':
    unittest.main()
