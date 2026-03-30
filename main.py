import os
import warnings

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("GLOG_minloglevel", "3")
os.environ.setdefault("ABSL_LOG_LEVEL", "3")
warnings.filterwarnings("ignore")

import threading
import queue
import time
from config.settings           import DEVICE, SCREEN_WIDTH, SCREEN_HEIGHT
from gaze.calibration          import GazeMeasurement
from gaze.camera               import Camera
from gaze.detector             import GazeDetector
from gaze.smoother             import GazeSmoother
from gaze.estimator            import GazeEstimator
from control.mouse_controller  import MouseController
from control.dwell_handler     import DwellHandler
from keyboard.virtual_keyboard import VirtualKeyboard
from ui.calibration_ui         import CalibrationUI
from ui.feedback               import FeedbackManager
from keyboard.key_layout       import get_keyboard_y
from utils.logger              import get_logger

logger = get_logger(__name__)


class SharedState:
    def __init__(self):
        self.lock        = threading.Lock()
        self.gaze_queue  = queue.Queue(maxsize=2)
        self.running     = True
        self.frame       = None
        self.debug_info  = {}
        self.dwell_prog  = 0.0
        self.frame_gaze  = (0, 0)
        self.flashing    = False
        self.latest_measurement = None
        self.calibration_profile = None
        self.calibrated = False


def gaze_to_frame(nx, ny, fw, fh):
    return int(nx * fw), int(ny * fh)


def gaze_thread(state: SharedState, camera: Camera):
    from config.settings import FRAME_WIDTH, FRAME_HEIGHT

    detector  = GazeDetector()
    smoother  = GazeSmoother()
    estimator = GazeEstimator()
    mouse     = MouseController()
    dwell     = DwellHandler()
    feedback  = FeedbackManager()

    try:
        logger.info("Gaze thread running.")

        while state.running:
            frame = camera.read()
            if frame is None:
                continue

            gaze_data = detector.process(frame)

            if gaze_data is None:
                with state.lock:
                    state.frame = frame.copy()
                continue

            left_ratio  = gaze_data["left_eye_ratio"]
            right_ratio = gaze_data["right_eye_ratio"]
            raw_nx, raw_ny = gaze_data["raw_gaze"]
            face_nx, face_ny = gaze_data["face_anchor"]
            yaw         = gaze_data["yaw"]
            pitch       = gaze_data["pitch"]
            measurement = GazeMeasurement(
                raw_nx=raw_nx,
                raw_ny=raw_ny,
                face_nx=face_nx,
                face_ny=face_ny,
                yaw=yaw,
                pitch=pitch,
                timestamp=time.time(),
            )

            with state.lock:
                profile = state.calibration_profile
                calibrated = state.calibrated

            if calibrated and profile is not None:
                nx, ny = profile.map_to_normalized(measurement)
                nx, ny = smoother.smooth(nx, ny)
                screen_x, screen_y = estimator.estimate(nx, ny)

                try:
                    if state.gaze_queue.full():
                        state.gaze_queue.get_nowait()
                    state.gaze_queue.put_nowait((screen_x, screen_y))
                except Exception:
                    pass

                mouse.move(screen_x, screen_y)

                if screen_y < get_keyboard_y():
                    clicked = dwell.update(screen_x, screen_y)
                    if clicked:
                        mouse.click(screen_x, screen_y)
                        feedback.trigger()
                else:
                    dwell.reset()
            else:
                nx, ny = 0.5, 0.5
                screen_x, screen_y = estimator.estimate(nx, ny)
                dwell.reset()

            left_iris = gaze_data["left_iris"]
            right_iris = gaze_data["right_iris"]
            frame_gaze = (
                int((left_iris[0] + right_iris[0]) / 2),
                int((left_iris[1] + right_iris[1]) / 2),
            )
            debug_info = {
                "gaze" : f"{nx:.2f}, {ny:.2f}",
                "raw"  : f"{raw_nx:.2f}, {raw_ny:.2f}",
                "screen": f"{screen_x}, {screen_y}",
                "dwell" : f"{dwell.progress:.0%}",
                "yaw"   : f"{yaw:.1f}°",
                "pitch" : f"{pitch:.1f}°",
                "L eye" : f"{left_ratio:.2f}",
                "R eye" : f"{right_ratio:.2f}",
                "mode"  : "live" if calibrated else "calibrating",
                "device": str(DEVICE),
            }

            with state.lock:
                state.frame      = frame.copy()
                state.debug_info = debug_info
                state.dwell_prog = dwell.progress
                state.frame_gaze = frame_gaze
                state.flashing   = feedback.is_flashing
                state.latest_measurement = measurement

    except Exception as e:
        logger.error(f"Gaze thread error: {e}")
    finally:
        camera.stop()
        detector.close()
        logger.info("Gaze thread stopped.")


def main():
    logger.info(f"Starting GazeControl | Device: {DEVICE} | "
                f"Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    state = SharedState()
    camera = Camera()

    try:
        # macOS camera authorization must be triggered from the main thread.
        camera.start()
    except Exception as e:
        logger.error(f"Camera startup failed on main thread: {e}")
        return

    # Gaze in background
    t = threading.Thread(target=gaze_thread, args=(state, camera), daemon=True)
    t.start()

    calibration = CalibrationUI(state)
    profile = calibration.run()
    if profile is None:
        state.running = False
        t.join(timeout=3)
        logger.error("Calibration did not complete.")
        return

    with state.lock:
        state.calibration_profile = profile
        state.calibrated = True

    # Keyboard + preview on main thread
    keyboard = VirtualKeyboard(state)
    keyboard.start_main_thread(on_quit=lambda: setattr(state, 'running', False))

    state.running = False
    t.join(timeout=3)
    logger.info("Shutdown complete.")


if __name__ == "__main__":
    main()
