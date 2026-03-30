import time
import math
from utils.logger import get_logger
from config.settings import DWELL_TIME, DWELL_COOLDOWN, DWELL_RADIUS

logger = get_logger(__name__)


class DwellHandler:
    def __init__(self):
        self.dwell_start  = None
        self.dwell_x      = None
        self.dwell_y      = None
        self.last_trigger = 0.0
        self.progress     = 0.0
        logger.info("DwellHandler initialized.")

    def update(self, gaze_x: int, gaze_y: int) -> bool:
        now = time.time()

        if now - self.last_trigger < DWELL_COOLDOWN:
            self.progress = 0.0
            return False

        if self.dwell_x is None:
            self._reset_dwell(gaze_x, gaze_y, now)
            return False

        dist = math.hypot(gaze_x - self.dwell_x, gaze_y - self.dwell_y)

        if dist > DWELL_RADIUS:
            self._reset_dwell(gaze_x, gaze_y, now)
            return False

        elapsed       = now - self.dwell_start
        self.progress = min(elapsed / DWELL_TIME, 1.0)

        if elapsed >= DWELL_TIME:
            logger.debug(f"Dwell triggered at ({gaze_x}, {gaze_y})")
            self.last_trigger = now
            self._reset_dwell(gaze_x, gaze_y, now)
            return True

        return False

    def _reset_dwell(self, x: int, y: int, t: float):
        self.dwell_x     = x
        self.dwell_y     = y
        self.dwell_start = t
        self.progress    = 0.0

    def reset(self):
        self.dwell_x      = None
        self.dwell_y      = None
        self.dwell_start  = None
        self.last_trigger = 0.0
        self.progress     = 0.0
        logger.info("DwellHandler reset.")