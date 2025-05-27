import cv2
import sys
import time
import mediapipe as mp
import numpy as np
import pygame
from pygame.locals import *

class EyelightGame:
    def __init__(self):
        """Initialize the Eyelight game"""
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Eyelight Game")
        
        # Screen setup
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.fps = 30
        
        # Font setup
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Camera setup
        self.cap = None
        self.setup_camera()
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Eye landmarks indices (for MediaPipe Face Mesh)
        # Left eye indices
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        # Right eye indices
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        
        # Game state variables
        self.STATES = {
            'WAITING': 0,
            'GREEN_LIGHT': 1,
            'RED_LIGHT': 2,
            'GAME_OVER': 3
        }
        self.current_state = self.STATES['WAITING']
        self.state_start_time = time.time()
        
        # Game timing settings (in seconds)
        self.green_light_duration = 5.0  # Green light duration
        self.red_light_duration = 3.0    # Red light duration
        self.countdown_duration = 3.0    # Initial countdown duration
        
        # Violation tracking
        self.violations = 0
        self.max_violations = 3
        
        # Game running flag
        self.running = True
        
    def setup_camera(self):
        """Setup webcam capture"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            sys.exit()
        return True
        
    def calculate_ear(self, landmarks, eye_indices):
        """
        Calculate Eye Aspect Ratio (EAR) for a given eye
        EAR = (h1 + h2) / (2 * w)
        where h1, h2 are vertical distances and w is horizontal distance between eye landmarks
        """
        # Get the coordinates of the specified landmarks
        points = [landmarks[idx] for idx in eye_indices]
        
        # Calculate vertical distances
        vertical_dist1 = self.distance(points[1], points[5])
        vertical_dist2 = self.distance(points[2], points[4])
        
        # Calculate horizontal distance
        horizontal_dist = self.distance(points[0], points[3])
        
        # Calculate EAR
        if horizontal_dist > 0:
            ear = (vertical_dist1 + vertical_dist2) / (2 * horizontal_dist)
        else:
            ear = 0.0
            
        return ear
    
    def distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_eyes_open(self, left_ear, right_ear, threshold=0.2):
        """Determine if eyes are open based on EAR values"""
        return left_ear > threshold and right_ear > threshold
        
    def detect_eyes(self):
        """Detect eyes and determine if they are open or closed"""
        # Read frame from webcam
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to capture image")
            return None, False, 0, 0
            
        # Flip frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image to detect facial landmarks
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            # Convert OpenCV image to Pygame surface
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            return frame, False, 0, 0  # No face detected
        
        # Get the first face detected
        face_landmarks = results.multi_face_landmarks[0]
        
        # Draw face mesh and eye contours
        # We'll keep the visualization in the OpenCV frame
        self.mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
        )
        
        self.mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
        )
        
        # Get normalized landmarks
        landmarks = face_landmarks.landmark
        
        # Calculate EAR for both eyes
        left_ear = self.calculate_ear(landmarks, self.LEFT_EYE_INDICES)
        right_ear = self.calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
        
        # Determine if eyes are open
        eyes_open = self.is_eyes_open(left_ear, right_ear)
        
        # Convert OpenCV image to Pygame surface
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Rotate and transpose to make it compatible with pygame
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        
        return frame, eyes_open, left_ear, right_ear
        
    def get_state_name(self, state):
        """Convert state value to name"""
        for name, value in self.STATES.items():
            if value == state:
                return name
        return "UNKNOWN"
        
    def update_game_state(self, current_time):
        """Update game state based on timers"""
        # Get time elapsed since the current state started
        elapsed_time = current_time - self.state_start_time
        
        if self.current_state == self.STATES['WAITING']:
            # In waiting state, start countdown
            if elapsed_time >= self.countdown_duration:
                self.current_state = self.STATES['GREEN_LIGHT']
                self.state_start_time = current_time
                
        elif self.current_state == self.STATES['GREEN_LIGHT']:
            # In green light state, switch to red light after duration
            if elapsed_time >= self.green_light_duration:
                self.current_state = self.STATES['RED_LIGHT']
                self.state_start_time = current_time
                
        elif self.current_state == self.STATES['RED_LIGHT']:
            # In red light state, switch to green light after duration
            if elapsed_time >= self.red_light_duration:
                self.current_state = self.STATES['GREEN_LIGHT']
                self.state_start_time = current_time
                
    def check_violations(self, eyes_open):
        """Check for rule violations based on game state"""
        # During red light, having eyes open is a violation
        if self.current_state == self.STATES['RED_LIGHT'] and eyes_open:
            self.violations += 1
            print(f"Violation detected! Total: {self.violations}/{self.max_violations}")
            
            if self.violations >= self.max_violations:
                self.current_state = self.STATES['GAME_OVER']
            return True
        return False
        
    def draw_game_elements(self, webcam_surface=None, eyes_open=False, left_ear=0, right_ear=0):
        """Draw all game elements on the Pygame screen"""
        # Fill the background
        self.screen.fill((0, 0, 0))  # Black background
        
        # Draw webcam feed if available
        if webcam_surface is not None:
            # Scale and position the webcam feed to fill most of the screen
            webcam_surface = pygame.transform.scale(webcam_surface, 
                                                   (self.screen_width, self.screen_height))
            self.screen.blit(webcam_surface, (0, 0))
        
        # Eye metrics display
        eye_metrics = f"Left EAR: {left_ear:.2f}, Right EAR: {right_ear:.2f}"
        eye_metrics_text = self.font_small.render(eye_metrics, True, (255, 255, 255))
        self.screen.blit(eye_metrics_text, (10, 50))
        
        # Eye state display
        eye_state = "Eyes: OPEN" if eyes_open else "Eyes: CLOSED"
        eye_state_color = (0, 255, 0) if eyes_open else (255, 0, 0)
        eye_state_text = self.font_medium.render(eye_state, True, eye_state_color)
        self.screen.blit(eye_state_text, (10, 10))
        
        # Show violations
        violation_text = f"Violations: {self.violations}/{self.max_violations}"
        violation_surface = self.font_medium.render(violation_text, True, (255, 0, 0))
        self.screen.blit(violation_surface, (10, 90))
        
        # Draw game state overlay
        self.draw_game_state_overlay(eyes_open)
        
        # Update the display
        pygame.display.flip()
        
    def draw_game_state_overlay(self, eyes_open):
        """Draw game state information and overlays"""
        if self.current_state == self.STATES['WAITING']:
            # Waiting state - display countdown
            elapsed_time = time.time() - self.state_start_time
            countdown = max(0, int(self.countdown_duration - elapsed_time))
            state_text = f"GET READY! Starting in {countdown}..."
            
            # Semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Black with alpha
            self.screen.blit(overlay, (0, 0))
            
            # Display countdown
            text_surface = self.font_large.render(state_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.screen_width // 2 - text_surface.get_width() // 2, 
                                           self.screen_height // 2 - text_surface.get_height() // 2))
            
        elif self.current_state == self.STATES['GREEN_LIGHT']:
            # Green light state
            state_text = "GREEN LIGHT!"
            instruction_text = "(Open your eyes to move)"
            
            # Semi-transparent green overlay if eyes are open
            if eyes_open:
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 255, 0, 50))  # Green with alpha
                self.screen.blit(overlay, (0, 0))
            
            # Display state and timer
            text_surface = self.font_large.render(state_text, True, (0, 255, 0))
            self.screen.blit(text_surface, (20, 150))
            
            text_surface = self.font_medium.render(instruction_text, True, (200, 255, 200))
            self.screen.blit(text_surface, (20, 200))
            
            # Timer display
            elapsed_time = time.time() - self.state_start_time
            remaining = max(0, self.green_light_duration - elapsed_time)
            timer_text = f"Time: {remaining:.1f}s"
            timer_surface = self.font_medium.render(timer_text, True, (0, 255, 0))
            self.screen.blit(timer_surface, (20, 250))
            
        elif self.current_state == self.STATES['RED_LIGHT']:
            # Red light state
            state_text = "RED LIGHT!"
            instruction_text = "(Close your eyes to freeze)"
            
            # Semi-transparent red overlay if eyes are open (violation)
            if eyes_open:
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 80))  # Red with alpha
                self.screen.blit(overlay, (0, 0))
            
            # Display state and timer
            text_surface = self.font_large.render(state_text, True, (255, 0, 0))
            self.screen.blit(text_surface, (20, 150))
            
            text_surface = self.font_medium.render(instruction_text, True, (255, 200, 200))
            self.screen.blit(text_surface, (20, 200))
            
            # Timer display
            elapsed_time = time.time() - self.state_start_time
            remaining = max(0, self.red_light_duration - elapsed_time)
            timer_text = f"Time: {remaining:.1f}s"
            timer_surface = self.font_medium.render(timer_text, True, (255, 0, 0))
            self.screen.blit(timer_surface, (20, 250))
            
        elif self.current_state == self.STATES['GAME_OVER']:
            # Game over state
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((100, 0, 0, 180))  # Red with alpha
            self.screen.blit(overlay, (0, 0))
            
            # Display game over text
            state_text = "GAME OVER!"
            text_surface = self.font_large.render(state_text, True, (255, 0, 0))
            self.screen.blit(text_surface, (self.screen_width // 2 - text_surface.get_width() // 2, 
                                           self.screen_height // 2 - text_surface.get_height() // 2 - 50))
            
            # Display restart instructions
            instructions = "Press SPACE to restart game"
            instructions_text = self.font_medium.render(instructions, True, (255, 255, 255))
            self.screen.blit(instructions_text, (self.screen_width // 2 - instructions_text.get_width() // 2, 
                                                self.screen_height // 2 + 50))
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.current_state = self.STATES['WAITING']
        self.state_start_time = time.time()
        self.violations = 0
        print("Game reset!")
    
    def run(self):
        """Main game loop"""
        print("Starting Eyelight Game - Press ESC to quit, SPACE to restart")
        
        # Main game loop
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    elif event.key == K_SPACE and self.current_state == self.STATES['GAME_OVER']:
                        self.reset_game()
            
            # Get current time for state management
            current_time = time.time()
            
            # Process webcam frame to detect eyes
            webcam_surface, eyes_open, left_ear, right_ear = self.detect_eyes()
            
            # Update game state based on timers
            self.update_game_state(current_time)
            
            # Check for violations
            if self.current_state not in [self.STATES['WAITING'], self.STATES['GAME_OVER']]:
                self.check_violations(eyes_open)
            
            # Draw game elements
            self.draw_game_elements(webcam_surface, eyes_open, left_ear, right_ear)
            
            # Cap the frame rate
            self.clock.tick(self.fps)
                
        # Release resources
        self.cleanup()
    
    def cleanup(self):
        """Release resources"""
        if self.cap is not None:
            self.cap.release()
        pygame.quit()
        print("Eyelight Game closed")


if __name__ == "__main__":
    # Create and run game
    game = EyelightGame()
    try:
        game.run()
    except Exception as e:
        print(f"Error occurred: {e}")
        game.cleanup()
        sys.exit(1)
