import json
import os
import time
from .logger import logger

DATA_FILE = "data/guardian_data.json"

class Storage:
    def __init__(self):
        self.data = {
            "users": {}, # user_id -> {violations: 0, msg_count: 0, join_time: 0, verified: False}
            "settings": {"raid_mode": False}
        }
        self.ensure_data_dir()
        self.load()

    def ensure_data_dir(self):
        if not os.path.exists("data"):
            os.makedirs("data")

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load data: {e}. Starting fresh.")

    def save(self):
        try:
            self.ensure_data_dir()
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save data: {e}")

    def get_user(self, user_id):
        str_id = str(user_id)
        if str_id not in self.data["users"]:
            self.data["users"][str_id] = {
                "violations": 0,
                "msg_count": 0,
                "join_time": time.time(),
                "verified": False
            }
        return self.data["users"][str_id]

    def update_user(self, user_id, **kwargs):
        user = self.get_user(user_id)
        for k, v in kwargs.items():
            user[k] = v
        self.save()

    def add_violation(self, user_id):
        user = self.get_user(user_id)
        user["violations"] += 1
        self.save()
        return user["violations"]

    def increment_msg_count(self, user_id):
        user = self.get_user(user_id)
        user["msg_count"] += 1
        self.save()
        return user["msg_count"]

    def set_verified(self, user_id, status=True):
        self.update_user(user_id, verified=status)

    def is_verified(self, user_id):
        return self.get_user(user_id)["verified"]

storage = Storage()
