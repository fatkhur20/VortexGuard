from .logger import logger
from .storage import storage

class MemberLifecycle:
    def __init__(self):
        self.pending_users = set()

    def add_new_member(self, user_id):
        """
        Mark a new member as pending verification.
        """
        self.pending_users.add(user_id)
        # Reset verification in storage
        storage.set_verified(user_id, False)
        logger.info(f"User {user_id} added to pending verification.")

    def verify_member(self, user_id):
        """
        Mark a member as verified.
        """
        if user_id in self.pending_users:
            self.pending_users.remove(user_id)
        storage.set_verified(user_id, True)
        logger.info(f"User {user_id} verified.")

    def is_verified(self, user_id):
        """
        Check if a user is verified.
        """
        return storage.is_verified(user_id)

    def is_pending(self, user_id):
        return user_id in self.pending_users

member_lifecycle = MemberLifecycle()
