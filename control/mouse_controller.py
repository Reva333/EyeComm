import pyautogui
from utils.logger import get_logger
from config.settings import CURSOR_DEADZONE, SCREEN_WIDTH, SCREEN_HEIGHT

logger = get_logger(__name__)

pyautogui.FAILSAFE = False  # we handle bounds via clamp_to_screen
pyautogui.PAUSE    = 0.0


class MouseController:
    def __init__(self):
        self.last_position = None
        logger.info("MouseController initialized.")

    def move(self, x: int, y: int):
        try:
            if self.last_position is not None:
                px, py = self.last_position
                if ((x - px) ** 2 + (y - py) ** 2) ** 0.5 < CURSOR_DEADZONE:
                    return

            pyautogui.moveTo(x, y, duration=0.0)
            self.last_position = (x, y)
        except Exception as e:
            logger.warning(f"Mouse move failed: {e}")

    def click(self, x: int, y: int, button: str = "left"):
        try:
            pyautogui.click(x, y, button=button)
            logger.debug(f"Click [{button}] at ({x}, {y})")
        except Exception as e:
            logger.warning(f"Mouse click failed: {e}")

    def double_click(self, x: int, y: int):
        try:
            pyautogui.doubleClick(x, y)
            logger.debug(f"Double-click at ({x}, {y})")
        except Exception as e:
            logger.warning(f"Double-click failed: {e}")

    def scroll(self, clicks: int):
        try:
            pyautogui.scroll(clicks)
            logger.debug(f"Scroll {clicks}")
        except Exception as e:
            logger.warning(f"Scroll failed: {e}")

    def center(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.move(cx, cy)
