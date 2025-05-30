import pygame
import random

class AudioManager:
    def __init__(self):
        """Menangani pemutaran audio untuk permainan"""
        # Inisialisasi audio
        pygame.mixer.init()
        
        # Memuat file audio
        self.song = pygame.mixer.Sound('assets/sound/song.mp3')
        self.win_sound = pygame.mixer.Sound('assets/sound/win.mp3')
        self.lose_sound = pygame.mixer.Sound('assets/sound/lose.mp3')

        # Pelacakan status audio
        self.is_playing = False
        self.reset()
    
    def reset(self):
        """Mengatur ulang status audio manager"""
        self.stop_music()
        self.is_playing = False
    
    def start_music(self):
        """Mulai memutar lagu"""
        self.song.play()
        self.is_playing = True
        
    def stop_music(self):
        """Menghentikan lagu"""
        self.song.stop()
        self.is_playing = False
    
    def play_win_sound(self):
        """Memutar suara kemenangan"""
        self.stop_music()  # Menghentikan musik yang sedang diputar
        self.win_sound.play()
    
    def play_lose_sound(self):
        """Memutar suara kekalahan"""
        self.stop_music()
        self.lose_sound.play()

    def check_music_status(self):
        """Memeriksa apakah musik masih diputar"""
        if self.is_playing and not pygame.mixer.get_busy():
            # Musik baru saja berhenti secara alami
            self.is_playing = False
            print("Lagu selesai secara alami")
            return True  # Musik baru saja berhenti
        return False  # Tidak ada perubahan status musik
    
    def should_continue_playing(self):
        """Selalu lanjutkan memutar lagu"""
        return True
