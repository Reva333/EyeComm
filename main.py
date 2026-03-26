import threading
import queue
from config.settings           import DEVICE, SCREEN_WIDTH, SCREEN_HEIGHT
from gaze.camera               import Camera
from gaze.detector             import GazeDetector
from gaze.smoother             import GazeSmoother
from gaze.estimator            import GazeEstimator
from control.mouse_controller  import MouseController
from control.dwell_handler     import DwellHandler
from keyboard.virtual_keyboard import VirtualKeyboard
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


def gaze_to_frame(nx, ny, fw, fh):
    return int(nx * fw), int(ny * fh)


def gaze_thread(state: SharedState):
    from config.settings import FRAME_WIDTH, FRAME_HEIGHT

    camera    = Camera()
    detector  = GazeDetector()
    smoother  = GazeSmoother()
    estimator = GazeEstimator()
    mouse     = MouseController()
    dwell     = DwellHandler()
    feedback  = FeedbackManager()

    try:
        camera.start()
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

            nx, ny      = gaze_data["gaze_point"]
            left_ratio  = gaze_data["left_eye_ratio"]
            right_ratio = gaze_data["right_eye_ratio"]
            yaw         = gaze_data["yaw"]
            pitch       = gaze_data["pitch"]

            nx, ny = smoother.smooth(nx, ny)
            screen_x, screen_y = estimator.estimate(nx, ny)

            # Push to keyboard
            try:
                if state.gaze_queue.full():
                    state.gaze_queue.get_nowait()
                state.gaze_queue.put_nowait((screen_x, screen_y))
            except Exception:
                pass

            # Move mouse
            mouse.move(screen_x, screen_y)

            # Dwell — only above keyboard area
            if screen_y < get_keyboard_y():
                clicked = dwell.update(screen_x, screen_y)
                if clicked:
                    mouse.click(screen_x, screen_y)
                    feedback.trigger()
            else:
                dwell.reset()

            frame_gaze = gaze_to_frame(nx, ny, FRAME_WIDTH, FRAME_HEIGHT)
            debug_info = {
                "gaze" : f"{nx:.2f}, {ny:.2f}",
                "screen": f"{screen_x}, {screen_y}",
                "dwell" : f"{dwell.progress:.0%}",
                "yaw"   : f"{yaw:.1f}°",
                "pitch" : f"{pitch:.1f}°",
                "L eye" : f"{left_ratio:.2f}",
                "R eye" : f"{right_ratio:.2f}",
                "device": str(DEVICE),
            }

            with state.lock:
                state.frame      = frame.copy()
                state.debug_info = debug_info
                state.dwell_prog = dwell.progress
                state.frame_gaze = frame_gaze
                state.flashing   = feedback.is_flashing

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

    # Gaze in background
    t = threading.Thread(target=gaze_thread, args=(state,), daemon=True)
    t.start()

    # Keyboard + preview on main thread
    keyboard = VirtualKeyboard(state)
    keyboard.start_main_thread(on_quit=lambda: setattr(state, 'running', False))

    state.running = False
    t.join(timeout=3)
    logger.info("Shutdown complete.")


if __name__ == "__main__":
    main()