from .logger import logger

class MemberLifecycle:
    def __init__(self):
        self.verified_users = set()
        self.pending_users = set()

    def add_new_member(self, user_id):
        """
        Mark a new member as pending verification.
        """
        self.pending_users.add(user_id)
        # In case they rejoin, reset verification status
        if user_id in self.verified_users:
            self.verified_users.remove(user_id)
        logger.info(f"User {user_id} added to pending verification.")

    def verify_member(self, user_id):
        """
        Mark a member as verified.
        """
        if user_id in self.pending_users:
            self.pending_users.remove(user_id)
        self.verified_users.add(user_id)
        logger.info(f"User {user_id} verified.")

    def is_verified(self, user_id):
        """
        Check if a user is verified.
        """
        return user_id in self.verified_users

    def is_pending(self, user_id):
        return user_id in self.pending_users

member_lifecycle = MemberLifecycle()
