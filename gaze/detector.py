import cv2
import mediapipe as mp
from mediapipe.python.solutions import face_mesh as mp_face_mesh
import numpy as np
from utils.logger import get_logger

logger = get_logger(__name__)

LEFT_IRIS  = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
LEFT_EYE   = [33, 160, 158, 133, 153, 144]
RIGHT_EYE  = [362, 385, 387, 263, 373, 380]

LEFT_EYE_LEFT_CORNER  = 33
LEFT_EYE_RIGHT_CORNER = 133
LEFT_EYE_TOP          = 159
LEFT_EYE_BOTTOM       = 145

RIGHT_EYE_LEFT_CORNER  = 362
RIGHT_EYE_RIGHT_CORNER = 263
RIGHT_EYE_TOP          = 386
RIGHT_EYE_BOTTOM       = 374

MODEL_POINTS = np.array([
    (0.0,    0.0,    0.0),
    (0.0,   -330.0, -65.0),
    (-225.0, 170.0, -135.0),
    (225.0,  170.0, -135.0),
    (-150.0,-150.0, -125.0),
    (150.0, -150.0, -125.0),
], dtype=np.float64)

POSE_LANDMARK_IDS = [1, 152, 33, 263, 61, 291]


class GazeDetector:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self._yaw_history   = []
        self._pitch_history = []
        self._history_len   = 5
        logger.info("GazeDetector initialized with MediaPipe FaceMesh + Head Pose.")

    def process(self, frame: np.ndarray) -> dict | None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.face_mesh.process(rgb)
        rgb.flags.writeable = True

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]

        def lm(idx):
            return landmarks[idx].x * w, landmarks[idx].y * h

        def iris_center(indices):
            pts = [(landmarks[i].x * w, landmarks[i].y * h) for i in indices]
            return np.mean([p[0] for p in pts]), np.mean([p[1] for p in pts])

        # --- Iris centers ---
        left_cx,  left_cy  = iris_center(LEFT_IRIS)
        right_cx, right_cy = iris_center(RIGHT_IRIS)

        # --- Eye bounding boxes ---
        left_x0,  _ = lm(LEFT_EYE_LEFT_CORNER)
        left_x1,  _ = lm(LEFT_EYE_RIGHT_CORNER)
        _,  left_y0 = lm(LEFT_EYE_TOP)
        _,  left_y1 = lm(LEFT_EYE_BOTTOM)

        right_x0, _  = lm(RIGHT_EYE_LEFT_CORNER)
        right_x1, _  = lm(RIGHT_EYE_RIGHT_CORNER)
        _, right_y0  = lm(RIGHT_EYE_TOP)
        _, right_y1  = lm(RIGHT_EYE_BOTTOM)

        left_eye_center_x = (left_x0 + left_x1) / 2.0
        left_eye_center_y = (left_y0 + left_y1) / 2.0
        right_eye_center_x = (right_x0 + right_x1) / 2.0
        right_eye_center_y = (right_y0 + right_y1) / 2.0

        # --- Relative iris position within eye socket ---
        def relative_pos(iris, x0, x1, y0, y1):
            rx = (iris[0] - x0) / (x1 - x0 + 1e-6)
            ry = (iris[1] - y0) / (y1 - y0 + 1e-6)
            return rx, ry

        left_rx,  left_ry  = relative_pos(
            (left_cx,  left_cy),  left_x0,  left_x1,  left_y0,  left_y1)
        right_rx, right_ry = relative_pos(
            (right_cx, right_cy), right_x0, right_x1, right_y0, right_y1)

        # --- Raw gaze ---
        raw_nx = (left_rx + right_rx) / 2.0
        raw_ny = (left_ry + right_ry) / 2.0

        face_nx = ((left_eye_center_x + right_eye_center_x) / 2.0) / w
        face_ny = ((left_eye_center_y + right_eye_center_y) / 2.0) / h

        # --- Head pose ---
        yaw, pitch = self._estimate_head_pose(landmarks, w, h)
        yaw, pitch = self._smooth_head_pose(yaw, pitch)

        # --- Eye openness ---
        def eye_ratio(indices):
            pts   = [(landmarks[i].x * w, landmarks[i].y * h) for i in indices]
            vert  = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
            horiz = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
            return float(vert / (horiz + 1e-6))

        left_ratio  = eye_ratio(LEFT_EYE)
        right_ratio = eye_ratio(RIGHT_EYE)

        return {
            "left_iris":       (int(left_cx),  int(left_cy)),
            "right_iris":      (int(right_cx), int(right_cy)),
            "left_eye_ratio":  left_ratio,
            "right_eye_ratio": right_ratio,
            "raw_gaze":        (raw_nx, raw_ny),
            "face_anchor":     (face_nx, face_ny),
            "yaw":             yaw,
            "pitch":           pitch,
            "landmarks":       landmarks
        }

    def _estimate_head_pose(
        self,
        landmarks,
        w: int,
        h: int
    ) -> tuple[float, float]:
        image_points = np.array([
            (landmarks[idx].x * w, landmarks[idx].y * h)
            for idx in POSE_LANDMARK_IDS
        ], dtype=np.float64)

        focal_length  = float(w)
        camera_matrix = np.array([
            [focal_length, 0.0,          w / 2.0],
            [0.0,          focal_length, h / 2.0],
            [0.0,          0.0,          1.0    ]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rotation_vec, _ = cv2.solvePnP(
            MODEL_POINTS,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return 0.0, 0.0

        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        sy    = np.sqrt(rotation_mat[0, 0] ** 2 + rotation_mat[1, 0] ** 2)
        pitch = float(np.degrees(np.arctan2(-rotation_mat[2, 0], sy)))
        yaw   = float(np.degrees(np.arctan2(rotation_mat[1, 0], rotation_mat[0, 0])))

        return yaw, pitch

    def _smooth_head_pose(
        self,
        yaw: float,
        pitch: float
    ) -> tuple[float, float]:
        self._yaw_history.append(yaw)
        self._pitch_history.append(pitch)

        if len(self._yaw_history) > self._history_len:
            self._yaw_history.pop(0)
            self._pitch_history.pop(0)

        return (
            float(np.mean(self._yaw_history)),
            float(np.mean(self._pitch_history))
        )

    def close(self):
        self.face_mesh.close()
        logger.info("GazeDetector closed.")
