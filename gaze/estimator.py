from utils.logger import get_logger
from utils.screen_utils import clamp_to_screen
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

logger = get_logger(__name__)


class GazeEstimator:
    def __init__(self):
        logger.info("GazeEstimator initialized.")

    def estimate(self, nx: float, ny: float) -> tuple[int, int]:
        nx_scaled = max(0.0, min(1.0, nx))
        ny_scaled = max(0.0, min(1.0, ny))

        sx = int(nx_scaled * SCREEN_WIDTH)
        sy = int(ny_scaled * SCREEN_HEIGHT)
        return clamp_to_screen(sx, sy)
