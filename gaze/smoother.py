import numpy as np
from filterpy.kalman import KalmanFilter
from config.settings import (
    FAST_SMOOTHING_FACTOR,
    KALMAN_MEASUREMENT_NOISE,
    KALMAN_PROCESS_NOISE,
    SMALL_MOVEMENT_THRESHOLD,
    SMOOTHING_FACTOR,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class GazeSmoother:
    def __init__(self):
        self.kf = self._build_kalman()
        self.ewma = EWMASmoother()
        self.initialized = False
        logger.info("GazeSmoother initialized with Kalman filter.")

    def _build_kalman(self) -> KalmanFilter:
        kf = KalmanFilter(dim_x=4, dim_z=2)

        kf.F = np.array([[1, 0, 1, 0],
                         [0, 1, 0, 1],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype=float)

        kf.H = np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0]], dtype=float)

        kf.R *= KALMAN_MEASUREMENT_NOISE
        kf.Q *= KALMAN_PROCESS_NOISE
        kf.P *= 10

        return kf

    def smooth(self, x: float, y: float) -> tuple[float, float]:
        if not self.initialized:
            self.kf.x = np.array([[x], [y], [0], [0]], dtype=float)
            self.initialized = True
            return self.ewma.smooth(x, y)

        self.kf.predict()
        self.kf.update(np.array([[x], [y]], dtype=float))

        filtered_x = float(self.kf.x[0][0])
        filtered_y = float(self.kf.x[1][0])
        return self.ewma.smooth(filtered_x, filtered_y)

    def reset(self):
        self.kf = self._build_kalman()
        self.ewma.reset()
        self.initialized = False
        logger.info("GazeSmoother reset.")


class EWMASmoother:
    def __init__(self):
        self.x = None
        self.y = None

    def smooth(self, x: float, y: float) -> tuple[float, float]:
        if self.x is None:
            self.x, self.y = x, y
        else:
            movement = np.hypot(x - self.x, y - self.y)
            alpha = (
                FAST_SMOOTHING_FACTOR
                if movement > SMALL_MOVEMENT_THRESHOLD
                else SMOOTHING_FACTOR
            )
            self.x = alpha * self.x + (1 - alpha) * x
            self.y = alpha * self.y + (1 - alpha) * y
        return self.x, self.y

    def reset(self):
        self.x = None
        self.y = None
