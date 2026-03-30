import time
from utils.logger import get_logger

logger = get_logger(__name__)


class FeedbackManager:
    def __init__(self, flash_duration: float = 0.15):
        self.flash_duration = flash_duration
        self._flash_start   = 0.0
        self._flashing      = False
        logger.info("FeedbackManager initialized.")

    def trigger(self):
        self._flash_start = time.time()
        self._flashing    = True
        logger.debug("Feedback triggered.")

    @property
    def is_flashing(self) -> bool:
        if not self._flashing:
            return False
        if time.time() - self._flash_start > self.flash_duration:
            self._flashing = False
            return False
        return True

    def reset(self):
        self._flashing = False
        logger.info("FeedbackManager reset.")