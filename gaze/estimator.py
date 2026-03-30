import numpy as np
from utils.logger import get_logger
from utils.screen_utils import clamp_to_screen
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    GAZE_X_MIN, GAZE_X_MAX,
    GAZE_Y_MIN, GAZE_Y_MAX
)

logger = get_logger(__name__)


class GazeEstimator:
    def __init__(self):
        logger.info("GazeEstimator initialized.")

    def estimate(self, nx: float, ny: float) -> tuple[int, int]:
        # Remap iris range → full screen
        nx_scaled = (nx - GAZE_X_MIN) / (GAZE_X_MAX - GAZE_X_MIN)
        ny_scaled = (ny - GAZE_Y_MIN) / (GAZE_Y_MAX - GAZE_Y_MIN)

        nx_scaled = max(0.0, min(1.0, nx_scaled))
        ny_scaled = max(0.0, min(1.0, ny_scaled))

        sx = int(nx_scaled * SCREEN_WIDTH)
        # Invert the Y-axis so looking up (lower ny or higher ny depending on camera) moves cursor up
        sy = int((1.0 - ny_scaled) * SCREEN_HEIGHT)
        return clamp_to_screen(sx, sy)