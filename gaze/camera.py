import cv2
from utils.logger import get_logger
from config.settings import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, CAMERA_FPS

logger = get_logger(__name__)


class Camera:
    def __init__(self):
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        if not self.cap.isOpened():
            logger.error("Could not open camera.")
            raise RuntimeError("Camera not accessible.")

        logger.info(f"Camera started at index {CAMERA_INDEX} "
                    f"({FRAME_WIDTH}x{FRAME_HEIGHT} @ {CAMERA_FPS}fps)")

    def read(self):
        if self.cap is None:
            raise RuntimeError("Camera not started. Call start() first.")
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera.")
            return None
        return frame

    def stop(self):
        if self.cap:
            self.cap.release()
            logger.info("Camera released.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()