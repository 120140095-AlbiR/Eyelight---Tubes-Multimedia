import cv2
import numpy as np
import mediapipe as mp
import pygame

class EyeDetector:
    def __init__(self):
        # Inisialisasi MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Indeks landmark mata (untuk MediaPipe Face Mesh)
        # Indeks mata kiri
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]        # Indeks mata kanan
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        
    def setup_camera(self):
        """Mengatur akses kamera webcam"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Tidak dapat membuka webcam")
            return None
        return cap
        
    def calculate_ear(self, landmarks, eye_indices):
        """
        Menghitung Eye Aspect Ratio (EAR) untuk mata tertentu
        EAR = (h1 + h2) / (2 * w)
        dimana h1, h2 adalah jarak vertikal dan w adalah jarak horizontal antara landmark mata
        """
        # Mendapatkan koordinat landmark yang ditentukan
        points = [landmarks[idx] for idx in eye_indices]
        
        # Menghitung jarak vertikal
        vertical_dist1 = self.distance(points[1], points[5])
        vertical_dist2 = self.distance(points[2], points[4])
        
        # Menghitung jarak horizontal
        horizontal_dist = self.distance(points[0], points[3])
        
        # Menghitung EAR
        if horizontal_dist > 0:
            ear = (vertical_dist1 + vertical_dist2) / (2 * horizontal_dist)
        else:
            ear = 0.0
            
        return ear
    
    def distance(self, point1, point2):
        """Menghitung jarak Euclidean antara dua titik"""
        return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_eyes_open(self, left_ear, right_ear, threshold=0.3):
        """Menentukan apakah mata terbuka berdasarkan nilai EAR"""
        return left_ear > threshold and right_ear > threshold
    
    def detect_eyes(self, cap):
        """Mendeteksi mata dan menentukan apakah mata terbuka atau tertutup"""
        if cap is None:
            return None, False, 0, 0
              # Membaca frame dari webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Gagal menangkap gambar")
            return None, False, 0, 0
            
        # Membalik frame secara horizontal untuk efek cermin
        frame = cv2.flip(frame, 1)
        
        # Mengkonversi gambar BGR menjadi RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Memproses gambar untuk mendeteksi landmark wajah
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            # Mengkonversi gambar OpenCV menjadi surface Pygame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            return frame, False, 0, 0  # Tidak ada wajah terdeteksi
        
        # Mendapatkan wajah pertama yang terdeteksi
        face_landmarks = results.multi_face_landmarks[0]
          # Menggambar mesh wajah dan kontur mata
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
        
        # Mendapatkan landmark yang ternormalisasi
        landmarks = face_landmarks.landmark
        
        # Menghitung EAR untuk kedua mata
        left_ear = self.calculate_ear(landmarks, self.LEFT_EYE_INDICES)
        right_ear = self.calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
        
        # Menentukan apakah mata terbuka
        eyes_open = self.is_eyes_open(left_ear, right_ear)
        
        # Mengkonversi gambar OpenCV menjadi surface Pygame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Memutar dan mentranspose untuk membuat kompatibel dengan pygame
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        
        return frame, eyes_open, left_ear, right_ear
