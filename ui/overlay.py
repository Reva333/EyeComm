import cv2
import numpy as np
from utils.logger import get_logger

logger = get_logger(__name__)

COLOR_GAZE_DOT   = (0, 255, 0)
COLOR_DWELL_RING = (0, 200, 255)
COLOR_DWELL_DONE = (0, 255, 100)
COLOR_TEXT       = (255, 255, 255)
COLOR_DEBUG_BG   = (0, 0, 0)


class Overlay:
    def __init__(self, show_debug: bool = True):
        self.show_debug = show_debug
        logger.info("Overlay initialized.")

    def draw(
        self,
        frame: np.ndarray,
        gaze_px: tuple[int, int],
        dwell_progress: float = 0.0,
        debug_info: dict | None = None
    ) -> np.ndarray:
        out = frame.copy()
        x, y = gaze_px

        # Gaze dot
        cv2.circle(out, (x, y), 6, COLOR_GAZE_DOT, -1)
        cv2.circle(out, (x, y), 8, COLOR_GAZE_DOT, 1)

        # Dwell ring
        if dwell_progress > 0.0:
            radius = 24
            angle  = int(360 * dwell_progress)
            color  = COLOR_DWELL_DONE if dwell_progress >= 1.0 else COLOR_DWELL_RING
            cv2.ellipse(out, (x, y), (radius, radius),
                        -90, 0, angle, color, 3)

        # Debug panel
        if self.show_debug and debug_info:
            self._draw_debug(out, debug_info)

        return out

    def _draw_debug(self, frame: np.ndarray, info: dict):
        padding = 8
        line_h  = 20
        lines   = [f"{k}: {v}" for k, v in info.items()]
        panel_h = padding * 2 + line_h * len(lines)

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (300, panel_h), COLOR_DEBUG_BG, -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        for i, line in enumerate(lines):
            cy = padding + (i + 1) * line_h
            cv2.putText(frame, line, (padding, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT, 1)