# filepath: c:\Users\4lb17\Documents\buat kuliah\Sistem teknologi multimedia\tubes\Eyelight test 1\eyelight_game.py
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_SPACE, K_UP, K_DOWN, K_RETURN, RESIZABLE, VIDEORESIZE
import cv2
import time
import sys
import os

from eye_detector import EyeDetector
from audio_manager import AudioManager
from game_states import GameStateManager
from ui_renderer import UIRenderer

class EyelightGame:
    def __init__(self, screen_width=800, screen_height=600):
        # Menginisialisasi Pygame dan mixer
        pygame.init()
        pygame.mixer.init()
        
        # Siapkan jendela permainan yang dapat diubah ukurannya
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height), RESIZABLE)
        pygame.display.set_caption("Eyelight Game")
        
        # Inisialisasi webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Kesalahan: Tidak dapat mengakses webcam!")
            sys.exit(1)
        
        # Inisialisasi modul permainan
        self.audio_manager = AudioManager()
        self.game_state_manager = GameStateManager(self.audio_manager)
        self.eye_detector = EyeDetector()
        self.ui_renderer = UIRenderer(self.screen, self.game_state_manager)
        
        # Variabel status permainan
        self.running = True
        
        print("Memulai Eyelight Game - Tekan ESC untuk keluar, SPASI untuk mengulang")
    
    def run(self):
        """Menjalankan loop utama permainan"""
        
        # Loop utama permainan
        while self.running:
            # Menangani event
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if self.game_state_manager.current_state == self.game_state_manager.STATES['START_MENU']:
                            self.running = False  # Keluar jika di menu awal
                        elif self.game_state_manager.current_state == self.game_state_manager.STATES['HOW_TO_PLAY']:
                            # Kembali ke menu utama jika di layar cara bermain
                            self.game_state_manager.current_state = self.game_state_manager.STATES['START_MENU']
                        else:
                            self.reset_game()  # Kembali ke menu jika dalam permainan
                    elif event.key == K_SPACE and (self.game_state_manager.current_state == self.game_state_manager.STATES['GAME_OVER'] or 
                                                  self.game_state_manager.current_state == self.game_state_manager.STATES['WIN']):
                        self.reset_game()
                    # Navigasi menu
                    elif self.game_state_manager.current_state == self.game_state_manager.STATES['START_MENU']:
                        if event.key == K_UP:
                            self.game_state_manager.select_menu_option("up")
                        elif event.key == K_DOWN:
                            self.game_state_manager.select_menu_option("down")
                        elif event.key == K_RETURN:
                            action = self.game_state_manager.activate_selected_option()
                            if action == "start_game":
                                self.game_state_manager.start_game()
                                print("Memulai permainan!")
                            elif action == "how_to_play":
                                print("Menampilkan cara bermain...")
                            elif action == "exit":
                                self.running = False
                                print("Keluar dari permainan...")
                    # Kembali dari layar cara bermain
                    elif self.game_state_manager.current_state == self.game_state_manager.STATES['HOW_TO_PLAY']:
                        if event.key == K_RETURN:
                            self.game_state_manager.current_state = self.game_state_manager.STATES['START_MENU']
                            print("Kembali ke menu utama...")
                elif event.type == VIDEORESIZE:
                    # Memperbarui ukuran layar ketika pengguna mengubah ukuran jendela
                    self.screen_width, self.screen_height = event.size
                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), RESIZABLE)
                    # Memperbarui background pada UI renderer
                    self.ui_renderer.update_background()
            
            # Mendapatkan waktu saat ini untuk manajemen status
            current_time = time.time()
            
            # Memproses frame webcam untuk mendeteksi mata
            webcam_surface, eyes_open, left_ear, right_ear = self.eye_detector.detect_eyes(self.cap)
            
            # Memperbarui status permainan berdasarkan timer
            self.game_state_manager.update_state(current_time)
            
            # Memperbarui posisi pemain (hanya jika tidak dalam status WIN atau GAME_OVER)
            if self.game_state_manager.current_state not in [self.game_state_manager.STATES['GAME_OVER'], 
                                                          self.game_state_manager.STATES['WIN'],
                                                          self.game_state_manager.STATES['START_MENU'],
                                                          self.game_state_manager.STATES['HOW_TO_PLAY']]:
                self.game_state_manager.update_player_position(eyes_open)
            
            # Memeriksa pelanggaran (mata terbuka selama RED_LIGHT)
            self.game_state_manager.check_violations(eyes_open)
            
            # Memeriksa kondisi menang
            self.game_state_manager.check_win_condition()
            
            # Render elemen permainan ke layar
            self.ui_renderer.draw_game_elements(webcam_surface, eyes_open, left_ear, right_ear)
            
            # Batasi pada 30 FPS
            pygame.time.delay(33)  # Sekitar 30 fps
        
        # Cleanup ketika permainan berakhir
        self.cleanup()
    
    def reset_game(self):
        """Mengatur ulang permainan ke status awal"""
        self.game_state_manager.reset()
        self.audio_manager.stop_music()
    
    def cleanup(self):
        """Membersihkan sumber daya dan keluar dengan rapi"""
        # Hentikan musik dan suara
        self.audio_manager.stop_music()
        
        # Lepaskan webcam dan sumber daya CV2
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Tutup Pygame
        pygame.quit()
        print("Game bersih ditutup!")

if __name__ == "__main__":
    game = EyelightGame()
    game.run()
