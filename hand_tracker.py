"""
hand_tracker.py

Handles:
- Webcam capture
- MediaPipe Hand Landmarker
- Index finger tracking
- Finger smoothing
- Finger velocity
- Finger trail
- Camera recovery
"""

import os
import time
import math
import urllib.request

import cv2
import mediapipe as mp
import pygame

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# MEDIAPIPE MODEL
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "hand_landmarker.task"
)

MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/"
    "hand_landmarker.task"
)


def download_model_if_missing():
    """
    Download the MediaPipe model if it does not exist.
    """

    if os.path.exists(MODEL_PATH):
        return

    print("Downloading hand_landmarker.task model...")

    try:

        urllib.request.urlretrieve(
            MODEL_URL,
            MODEL_PATH
        )

        print("Download complete.")

    except Exception as error:

        print(
            "Could not download MediaPipe model:"
        )

        print(error)

        raise


# ============================================================
# HAND TRACKER
# ============================================================

class HandTracker:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        # ----------------------------------------------------
        # Camera
        # ----------------------------------------------------

        self.cap = None

        self.camera_failures = 0
        self.max_camera_failures = 10

        self._open_camera()

        # ----------------------------------------------------
        # MediaPipe result
        # ----------------------------------------------------

        self.latest_result = None

        self.latest_result_time = 0

        # ----------------------------------------------------
        # Finger position
        # ----------------------------------------------------

        self.prev_finger_pos = None
        self.current_finger_pos = None

        self.last_raw_pos = None

        # Smoothed velocity
        self.velocity = (0.0, 0.0)

        # ----------------------------------------------------
        # Smoothing configuration
        # ----------------------------------------------------

        self.MIN_ALPHA = 0.30
        self.MAX_ALPHA = 0.95

        # Speed at which smoothing becomes more responsive
        self.SPEED_FOR_MAX_ALPHA = 45.0

        # Prevent extremely large tracking jumps
        self.MAX_POSITION_JUMP = 180.0

        # ----------------------------------------------------
        # Finger trail
        # ----------------------------------------------------

        self.trail = []

        self.max_trail_length = 18

        # ----------------------------------------------------
        # Async timestamp
        # ----------------------------------------------------

        self.frame_timestamp_ms = 0

        # ----------------------------------------------------
        # Camera frame processing
        # ----------------------------------------------------

        self.processing_width = 320
        self.processing_height = 240

        # ----------------------------------------------------
        # Result timeout
        # ----------------------------------------------------

        self.result_timeout = 0.35

        # ----------------------------------------------------
        # Initialize detector
        # ----------------------------------------------------

        download_model_if_missing()

        self._create_detector()

    # ========================================================
    # CAMERA
    # ========================================================

    def _open_camera(self):

        # Release old camera if necessary
        if self.cap is not None:

            try:
                self.cap.release()
            except Exception:
                pass

        self.cap = cv2.VideoCapture(0)

        # Camera resolution
        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height
        )

        # Try to reduce camera buffering
        try:

            self.cap.set(
                cv2.CAP_PROP_BUFFERSIZE,
                1
            )

        except Exception:
            pass

        # Reset failure counter
        self.camera_failures = 0

    # ========================================================
    # MEDIAPIPE DETECTOR
    # ========================================================

    def _create_detector(self):

        # Base model configuration
        base_options = python.BaseOptions(
            model_asset_path=MODEL_PATH
        )

        options = vision.HandLandmarkerOptions(

            base_options=base_options,

            # One hand is enough for this game
            num_hands=1,

            # Async processing
            running_mode=(
                vision.RunningMode.LIVE_STREAM
            ),

            # Detection confidence
            min_hand_detection_confidence=0.5,

            # Hand presence confidence
            min_hand_presence_confidence=0.5,

            # Tracking confidence
            min_tracking_confidence=0.55,

            # Callback
            result_callback=self._result_callback
        )

        self.detector = (
            vision.HandLandmarker
            .create_from_options(options)
        )

    # ========================================================
    # MEDIAPIPE CALLBACK
    # ========================================================

    def _result_callback(
        self,
        result,
        output_image,
        timestamp_ms
    ):
        """
        Called by MediaPipe when a new result
        becomes available.
        """

        self.latest_result = result

        self.latest_result_time = (
            time.monotonic()
        )

    # ========================================================
    # RESET TRACKING
    # ========================================================

    def _reset_tracking(self):

        self.prev_finger_pos = None
        self.current_finger_pos = None

        self.last_raw_pos = None

        self.velocity = (0.0, 0.0)

        self.trail.clear()

    # ========================================================
    # GET FRAME + FINGER
    # ========================================================

    def get_frame_and_finger(self):

        # ----------------------------------------------------
        # Read camera
        # ----------------------------------------------------

        success, frame = self.cap.read()

        if not success:

            self.camera_failures += 1

            # Remove old tracking data
            self._reset_tracking()

            # Try reopening camera
            if (
                self.camera_failures
                >= self.max_camera_failures
            ):

                print(
                    "Camera connection lost. "
                    "Trying to reconnect..."
                )

                self._open_camera()

            return (
                None,
                self.current_finger_pos,
                self.prev_finger_pos
            )

        self.camera_failures = 0

        # ----------------------------------------------------
        # Mirror camera
        # ----------------------------------------------------

        frame = cv2.flip(
            frame,
            1
        )

        # ----------------------------------------------------
        # Convert BGR -> RGB
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # ----------------------------------------------------
        # Resize for MediaPipe
        # ----------------------------------------------------

        small_frame = cv2.resize(
            rgb_frame,
            (
                self.processing_width,
                self.processing_height
            ),
            interpolation=cv2.INTER_LINEAR
        )

        # ----------------------------------------------------
        # Create MediaPipe image
        # ----------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=small_frame
        )

        # ----------------------------------------------------
        # Timestamp
        # ----------------------------------------------------

        # Use real monotonic milliseconds.
        # MediaPipe requires increasing timestamps.

        timestamp = int(
            time.monotonic() * 1000
        )

        # Make absolutely sure timestamp increases
        if timestamp <= self.frame_timestamp_ms:

            timestamp = (
                self.frame_timestamp_ms + 1
            )

        self.frame_timestamp_ms = timestamp

        # ----------------------------------------------------
        # Send frame asynchronously
        # ----------------------------------------------------

        try:

            self.detector.detect_async(
                mp_image,
                self.frame_timestamp_ms
            )

        except Exception:

            # Don't crash the game if MediaPipe
            # temporarily rejects a frame.
            pass

        # ----------------------------------------------------
        # Previous finger position
        # ----------------------------------------------------

        self.prev_finger_pos = (
            self.current_finger_pos
        )

        # ----------------------------------------------------
        # Check if result is still fresh
        # ----------------------------------------------------

        result_is_fresh = (
            self.latest_result is not None
            and (
                time.monotonic()
                - self.latest_result_time
            ) <= self.result_timeout
        )

        # ----------------------------------------------------
        # Process hand landmarks
        # ----------------------------------------------------

        if (
            result_is_fresh
            and self.latest_result.hand_landmarks
        ):

            # Landmark 8 = index finger tip
            index_tip = (
                self.latest_result
                .hand_landmarks[0][8]
            )

            # ------------------------------------------------
            # Convert normalized coordinates
            # to game coordinates
            # ------------------------------------------------

            raw_x = (
                index_tip.x
                * self.width
            )

            raw_y = (
                index_tip.y
                * self.height
            )

            raw_position = (
                raw_x,
                raw_y
            )

            # ------------------------------------------------
            # First detection
            # ------------------------------------------------

            if (
                self.current_finger_pos is None
                or self.last_raw_pos is None
            ):

                self.current_finger_pos = (
                    raw_position
                )

                self.last_raw_pos = (
                    raw_position
                )

                self.velocity = (
                    0.0,
                    0.0
                )

            else:

                # --------------------------------------------
                # Calculate raw movement
                # --------------------------------------------

                raw_vx = (
                    raw_x
                    - self.last_raw_pos[0]
                )

                raw_vy = (
                    raw_y
                    - self.last_raw_pos[1]
                )

                raw_speed = math.hypot(
                    raw_vx,
                    raw_vy
                )

                # --------------------------------------------
                # Ignore impossible jumps
                # --------------------------------------------

                if (
                    raw_speed
                    > self.MAX_POSITION_JUMP
                ):

                    # Treat this as a tracking glitch
                    self.last_raw_pos = (
                        raw_position
                    )

                    return (
                        self._create_surface(
                            rgb_frame
                        ),
                        self.current_finger_pos,
                        self.prev_finger_pos
                    )

                # --------------------------------------------
                # Smooth velocity
                # --------------------------------------------

                velocity_smoothing = 0.65

                self.velocity = (

                    self.velocity[0]
                    * velocity_smoothing
                    + raw_vx
                    * (1 - velocity_smoothing),

                    self.velocity[1]
                    * velocity_smoothing
                    + raw_vy
                    * (1 - velocity_smoothing)
                )

                # --------------------------------------------
                # Calculate speed
                # --------------------------------------------

                speed = math.hypot(
                    self.velocity[0],
                    self.velocity[1]
                )

                # --------------------------------------------
                # Adaptive smoothing
                # --------------------------------------------

                speed_factor = min(
                    1.0,
                    speed
                    / self.SPEED_FOR_MAX_ALPHA
                )

                alpha = (
                    self.MIN_ALPHA
                    + (
                        self.MAX_ALPHA
                        - self.MIN_ALPHA
                    )
                    * speed_factor
                )

                # --------------------------------------------
                # Smooth finger position
                # --------------------------------------------

                current_x = (
                    self.current_finger_pos[0]
                )

                current_y = (
                    self.current_finger_pos[1]
                )

                smoothed_x = (
                    current_x
                    + alpha
                    * (raw_x - current_x)
                )

                smoothed_y = (
                    current_y
                    + alpha
                    * (raw_y - current_y)
                )

                self.current_finger_pos = (
                    smoothed_x,
                    smoothed_y
                )

                self.last_raw_pos = (
                    raw_position
                )

        else:

            # ------------------------------------------------
            # No valid hand
            # ------------------------------------------------

            self.current_finger_pos = None

            self.last_raw_pos = None

            self.velocity = (
                0.0,
                0.0
            )

        # ----------------------------------------------------
        # Update trail
        # ----------------------------------------------------

        self._update_trail()

        # ----------------------------------------------------
        # Convert camera frame to Pygame
        # ----------------------------------------------------

        frame_surface = self._create_surface(
            rgb_frame
        )

        return (
            frame_surface,
            self.current_finger_pos,
            self.prev_finger_pos
        )

    # ========================================================
    # UPDATE TRAIL
    # ========================================================

    def _update_trail(self):

        if self.current_finger_pos is not None:

            self.trail.append(
                self.current_finger_pos
            )

            # Limit trail length
            if (
                len(self.trail)
                > self.max_trail_length
            ):

                self.trail.pop(0)

        else:

            # Fade trail when hand disappears
            if self.trail:

                self.trail.pop(0)

    # ========================================================
    # CREATE PYGAME SURFACE
    # ========================================================

    def _create_surface(self, rgb_frame):

        return pygame.surfarray.make_surface(
            rgb_frame.swapaxes(0, 1)
        )

    # ========================================================
    # DRAW FINGER TRAIL
    # ========================================================

    def draw_trail(self, surface):

        if len(self.trail) < 2:
            return

        trail_length = len(
            self.trail
        )

        for index in range(
            1,
            trail_length
        ):

            ratio = (
                index
                / trail_length
            )

            # Older part of trail is thinner
            core_thickness = max(
                2,
                int(
                    ratio * 10
                )
            )

            glow_thickness = (
                core_thickness + 8
            )

            p1 = (
                int(
                    self.trail[index - 1][0]
                ),
                int(
                    self.trail[index - 1][1]
                )
            )

            p2 = (
                int(
                    self.trail[index][0]
                ),
                int(
                    self.trail[index][1]
                )
            )

            # ------------------------------------------------
            # Outer glow
            # ------------------------------------------------

            pygame.draw.line(
                surface,
                (0, 150, 255),
                p1,
                p2,
                glow_thickness
            )

            # ------------------------------------------------
            # Inner trail
            # ------------------------------------------------

            pygame.draw.line(
                surface,
                (200, 255, 255),
                p1,
                p2,
                core_thickness
            )

        # ----------------------------------------------------
        # Glowing finger tip
        # ----------------------------------------------------

        last_point = self.trail[-1]

        p_last = (
            int(last_point[0]),
            int(last_point[1])
        )

        pygame.draw.circle(
            surface,
            (0, 150, 255),
            p_last,
            16,
            2
        )

        pygame.draw.circle(
            surface,
            (255, 255, 255),
            p_last,
            7
        )

    # ========================================================
    # RELEASE
    # ========================================================

    def release(self):

        # Camera
        if self.cap is not None:

            try:
                self.cap.release()
            except Exception:
                pass

        # MediaPipe detector
        try:

            if self.detector is not None:

                self.detector.close()

        except Exception:
            pass

        self._reset_tracking()