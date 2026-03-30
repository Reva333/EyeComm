import cv2
from Cocoa import NSDate, NSRunLoop
from AVFoundation import AVCaptureDevice, AVAuthorizationStatusAuthorized, AVMediaTypeVideo
from utils.logger import get_logger
from config.settings import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, CAMERA_FPS

logger = get_logger(__name__)

if hasattr(cv2, "setLogLevel"):
    cv2.setLogLevel(0)


class Camera:
    def __init__(self):
        self.cap = None

    def _ensure_permission(self):
        status = AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeVideo)
        if status == AVAuthorizationStatusAuthorized:
            return

        granted = {"value": False}

        def completion_handler(allowed):
            granted["value"] = bool(allowed)

        AVCaptureDevice.requestAccessForMediaType_completionHandler_(
            AVMediaTypeVideo,
            completion_handler
        )

        # Keep the main-thread run loop moving while the permission dialog resolves.
        deadline = NSDate.dateWithTimeIntervalSinceNow_(10.0)
        while NSDate.date().timeIntervalSinceDate_(deadline) < 0:
            NSRunLoop.currentRunLoop().runUntilDate_(
                NSDate.dateWithTimeIntervalSinceNow_(0.1)
            )
            status = AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeVideo)
            if status != 0:
                break

        if not granted["value"] and \
           AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeVideo) != \
           AVAuthorizationStatusAuthorized:
            logger.error("Camera permission not granted by macOS.")
            raise RuntimeError("Camera permission not granted.")

    def start(self):
        self._ensure_permission()
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
