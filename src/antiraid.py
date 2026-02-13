import time
from .config import RAID_TRIGGER_COUNT, RAID_TRIGGER_WINDOW
from .logger import logger

class AntiRaid:
    def __init__(self):
        self.join_timestamps = []
        self.is_raid_mode = False

    def register_join(self):
        """
        Records a user join and checks if raid thresholds are met.
        Returns True if raid mode should be enabled.
        """
        now = time.time()
        # Remove timestamps older than the window
        self.join_timestamps = [t for t in self.join_timestamps if now - t < RAID_TRIGGER_WINDOW]

        self.join_timestamps.append(now)

        logger.info(f"Join recorded. Recent joins: {len(self.join_timestamps)}")

        if len(self.join_timestamps) >= RAID_TRIGGER_COUNT:
            if not self.is_raid_mode:
                self.is_raid_mode = True
                return True
        # Logic to auto-disable raid mode could be time-based here
        # For now, we rely on manual reset or simple decay

        return False

    def is_safe(self):
        """
        Returns True if join rate has cooled down.
        """
        now = time.time()
        recent_joins = [t for t in self.join_timestamps if now - t < RAID_TRIGGER_WINDOW]
        return len(recent_joins) == 0

    def reset(self):
        self.join_timestamps = []
        self.is_raid_mode = False

anti_raid = AntiRaid()
