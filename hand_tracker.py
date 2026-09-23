"""
hand_tracker.py

Handles webcam feed and MediaPipe Tasks Vision hand processing with high-performance tracking.
"""
import os
import time
import urllib.request
import cv2
import mediapipe as mp
import pygame
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# The required model for the Hand Landmarker Task Vision API
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand_landmarker.task')
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'

def download_model_if_missing():
    """Downloads the MediaPipe hand landmarker model if it doesn't exist."""
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand_landmarker.task model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Download complete.")

class HandTracker:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Ensure the model exists before initializing the detector
        download_model_if_missing()
        
        # Initialize OpenCV video capture
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Container for asynchronous results
        self.latest_result = None
        
        # Callback for LIVE_STREAM mode
        def result_callback(result, output_image, timestamp_ms):
            self.latest_result = result
            
        # Initialize MediaPipe Tasks Vision Hand Landmarker for LIVE_STREAM
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=1,
            min_hand_detection_confidence=0.4,  # Lowered for faster initial detection
            min_hand_presence_confidence=0.4,   # Lowered to prioritize continuous tracking
            min_tracking_confidence=0.5,
            result_callback=result_callback
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # State variables for finger tracking
        self.prev_finger_pos = None
        self.current_finger_pos = None
        self.last_raw_pos = None
        self.velocity = (0.0, 0.0)
        
        # Finger trail for rendering
        self.trail = []
        self.max_trail_length = 15  # Reverted
        
        # Strictly increasing timestamp to prevent MediaPipe async crashes
        self.frame_timestamp_ms = 0
        
    def get_frame_and_finger(self):
        """
        Reads frame from webcam, processes MediaPipe hands asynchronously,
        updates trail, and returns the frame surface and current/prev finger positions.
        """
        success, frame = self.cap.read()
        if not success:
            # Graceful recovery: try to re-initialize camera if it drops
            self.cap.release()
            self.cap = cv2.VideoCapture(0)
            return None, self.current_finger_pos, self.prev_finger_pos
            
        # Mirror the frame
        frame = cv2.flip(frame, 1)
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Optimization: Resize frame before passing to MediaPipe to reduce CPU load
        # MediaPipe scales it internally anyway, doing it here saves inference time
        small_frame = cv2.resize(rgb_frame, (320, 240))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=small_frame)
        
        # Send to async detector with strictly monotonic timestamp
        self.frame_timestamp_ms += 1
        try:
            self.detector.detect_async(mp_image, self.frame_timestamp_ms)
        except Exception as e:
            # Handle potential collisions gracefully without breaking the thread
            pass
        
        # Process the latest available result
        self.prev_finger_pos = self.current_finger_pos
        
        if self.latest_result and self.latest_result.hand_landmarks:
            # Landmark 8 is the index finger tip
            index_tip = self.latest_result.hand_landmarks[0][8]
            raw_x = index_tip.x * self.width
            raw_y = index_tip.y * self.height
            
            # Apply adaptive predictive smoothing for low latency and zero jitter
            if self.current_finger_pos is None or self.last_raw_pos is None:
                self.current_finger_pos = (raw_x, raw_y)
                self.last_raw_pos = (raw_x, raw_y)
                self.velocity = (0.0, 0.0)
            else:
                # Raw velocity
                vx = raw_x - self.last_raw_pos[0]
                vy = raw_y - self.last_raw_pos[1]
                
                # Exponentially smooth velocity to avoid erratic predictions
                self.velocity = (self.velocity[0] * 0.5 + vx * 0.5, self.velocity[1] * 0.5 + vy * 0.5)
                
                import math
                speed = math.hypot(self.velocity[0], self.velocity[1])
                
                # Adaptive alpha for low latency and smooth stationary behavior
                speed_factor = max(0.0, min(1.0, speed / 40.0)) # Scaled up 20% faster
                # Base alpha 0.25 (smooths out jitter), max alpha 1.0 (literally zero latency)
                alpha = 0.25 + speed_factor * 0.75
                
                # No prediction, direct follow
                sm_x = self.current_finger_pos[0] + alpha * (raw_x - self.current_finger_pos[0])
                sm_y = self.current_finger_pos[1] + alpha * (raw_y - self.current_finger_pos[1])
                self.current_finger_pos = (sm_x, sm_y)
                self.last_raw_pos = (raw_x, raw_y)
        else:
            self.current_finger_pos = None
            self.last_raw_pos = None
                
        # Update trail
        if self.current_finger_pos:
            self.trail.append(self.current_finger_pos)
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)
        else:
            if len(self.trail) > 0:
                self.trail.pop(0)
                
        # Convert frame to Pygame surface
        # Pygame surface requires the frame to be rotated and transposed
        frame_surface = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
        
        return frame_surface, self.current_finger_pos, self.prev_finger_pos

    def draw_trail(self, surface):
        """
        Draws the smooth glowing trail following the finger.
        """
        if len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                # Dynamic thickness and alpha interpolation
                ratio = i / len(self.trail)
                core_thickness = int(ratio * 12)
                glow_thickness = core_thickness + 8
                
                p1 = (int(self.trail[i-1][0]), int(self.trail[i-1][1]))
                p2 = (int(self.trail[i][0]), int(self.trail[i][1]))
                
                # Draw outer glow
                pygame.draw.line(surface, (0, 150, 255), p1, p2, glow_thickness)
                # Draw inner core
                pygame.draw.line(surface, (200, 255, 255), p1, p2, core_thickness)
                
            # Draw the glowing tip
            p_last = (int(self.trail[-1][0]), int(self.trail[-1][1]))
            pygame.draw.circle(surface, (0, 150, 255), p_last, 16, 2)
            pygame.draw.circle(surface, (255, 255, 255), p_last, 10)

    def release(self):
        """Release the camera resources and close detector."""
        self.cap.release()
        try:
            self.detector.close()
        except:
            pass
