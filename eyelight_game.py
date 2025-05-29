import cv2
import sys
import time
import pygame
from pygame.locals import *

# Impor modul
from audio_manager import AudioManager
from eye_detector import EyeDetector
from game_states import GameStateManager
from ui_renderer import UIRenderer


class EyelightGame:
    def __init__(self):
        """Menginisialisasi permainan Eyelight"""
        # Menginisialisasi pygame
        pygame.init()
        pygame.display.set_caption("Eyelight Game")
        
        # Pengaturan layar
        self.screen_width = 1080
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.fps = 30
        
        # Menginisialisasi komponen
        self.audio_manager = AudioManager()
        self.eye_detector = EyeDetector()
        self.game_state_manager = GameStateManager(self.audio_manager)
        self.ui_renderer = UIRenderer(self.screen, self.game_state_manager)
        
        # Pengaturan kamera
        self.cap = self.eye_detector.setup_camera()
        if self.cap is None:
            print("Error: Tidak dapat membuka webcam")
            sys.exit(1)
        
        # Tanda permainan berjalan
        self.running = True
        
    def reset_game(self):
        """Mengatur ulang permainan ke status awal"""
        self.game_state_manager.reset()
        self.audio_manager.reset()
        print("Permainan diulang!")
    
    def run(self):
        """Loop utama permainan"""
        print("Memulai Eyelight Game - Tekan ESC untuk keluar, SPASI untuk mengulang")
        
        # Loop utama permainan
        while self.running:
            # Menangani event
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    elif event.key == K_SPACE and (self.game_state_manager.current_state == self.game_state_manager.STATES['GAME_OVER'] or 
                                                   self.game_state_manager.current_state == self.game_state_manager.STATES['WIN']):
                        self.reset_game()
            
            # Mendapatkan waktu saat ini untuk manajemen status
            current_time = time.time()
            
            # Memproses frame webcam untuk mendeteksi mata
            webcam_surface, eyes_open, left_ear, right_ear = self.eye_detector.detect_eyes(self.cap)
            
            # Memperbarui status permainan berdasarkan timer
            self.game_state_manager.update_state(current_time)
            
            # Memperbarui posisi pemain (hanya jika tidak dalam status WIN atau GAME_OVER)
            if self.game_state_manager.current_state not in [self.game_state_manager.STATES['GAME_OVER'], self.game_state_manager.STATES['WIN']]:
                self.game_state_manager.update_player_position(eyes_open)
                
                # Memeriksa kondisi kemenangan (hanya jika kita belum dalam status WIN)
                if self.game_state_manager.current_state != self.game_state_manager.STATES['WIN'] and self.game_state_manager.check_win_condition():
                    # Pemain telah menang, tidak perlu memeriksa pelanggaran
                    pass
                # Memeriksa pelanggaran (hanya jika tidak dalam status khusus)
                elif self.game_state_manager.current_state not in [self.game_state_manager.STATES['WAITING'], 
                                                                self.game_state_manager.STATES['GAME_OVER'], 
                                                                self.game_state_manager.STATES['WIN']]:
                    self.game_state_manager.check_violations(eyes_open)
            
            # Menggambar elemen permainan
            self.ui_renderer.draw_game_elements(webcam_surface, eyes_open, left_ear, right_ear)
            
            # Membatasi frame rate
            self.clock.tick(self.fps)
                
        # Melepaskan sumber daya
        self.cleanup()
    
    def cleanup(self):
        """Melepaskan sumber daya"""
        if self.cap is not None:
            self.cap.release()
        pygame.quit()
        print("Eyelight Game ditutup")


if __name__ == "__main__":
    # Membuat dan menjalankan permainan
    game = EyelightGame()
    try:
        game.run()
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        game.cleanup()
        sys.exit(1)
