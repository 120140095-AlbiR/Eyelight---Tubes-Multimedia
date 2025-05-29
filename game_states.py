import time
import random

class GameStateManager:
    def __init__(self, audio_manager):
        # Mendefinisikan status permainan
        self.STATES = {
            'WAITING': 0,
            'GREEN_LIGHT': 1,
            'GRACE_PERIOD': 2,
            'RED_LIGHT': 3,
            'GAME_OVER': 4,
            'WIN': 5
        }
        self.current_state = self.STATES['WAITING']
        self.state_start_time = time.time()
        
        # Pengaturan waktu permainan (dalam detik)
        self.green_light_duration = 5.0  # Durasi lampu hijau (akan diganti oleh musik)
        self.red_light_duration = 3.0    # Durasi lampu merah
        self.countdown_duration = 3.0    # Durasi hitung mundur awal
        self.grace_period_duration = 1.0  # Periode tenggang setelah musik berhenti
        
        # Menyimpan referensi audio manager
        self.audio_manager = audio_manager
        
        # Kemajuan pemain
        self.player_position = 0
        self.finish_line = 1000  # Posisi target untuk menang
        self.movement_speed = 2  # Seberapa cepat pemain bergerak ketika mata terbuka
        
    def get_state_name(self, state):
        """Mengkonversi nilai status menjadi nama"""
        for name, value in self.STATES.items():
            if value == state:
                return name
        return "TIDAK DIKENAL"
    
    def stop_current_music(self):
        """Paksa menghentikan musik yang sedang diputar dan memicu periode tenggang"""
        if self.current_state == self.STATES['GREEN_LIGHT'] and self.audio_manager.is_playing:
            print("Memaksa musik berhenti lebih awal")
            self.audio_manager.stop_music()
            self.current_state = self.STATES['GRACE_PERIOD']
            self.state_start_time = time.time()
            return True
        return False
    
    def update_state(self, current_time):
        """Memperbarui status permainan berdasarkan timer dan status musik"""
        # Mendapatkan waktu yang berlalu sejak status saat ini dimulai
        elapsed_time = current_time - self.state_start_time
        
        if self.current_state == self.STATES['WAITING']:
            # Dalam status menunggu, mulai hitungan mundur
            if elapsed_time >= self.countdown_duration:
                self.current_state = self.STATES['GREEN_LIGHT']
                self.state_start_time = current_time
                # Mulai memutar musik ketika beralih ke GREEN_LIGHT
                self.audio_manager.start_music()
                
        elif self.current_state == self.STATES['GREEN_LIGHT']:
            # Secara acak menghentikan musik (sekitar 0.95% kemungkinan per frame - sekitar 25% per detik pada 30fps)
            if self.audio_manager.is_playing and random.random() < 0.0095:
                print("Musik berhenti secara acak di tengah pemutaran!")
                self.stop_current_music()
            
            # Memeriksa apakah musik telah berhenti secara alami
            if self.audio_manager.check_music_status():
                # Musik berhenti, masuk periode tenggang
                self.current_state = self.STATES['GRACE_PERIOD']
                self.state_start_time = current_time
                
        elif self.current_state == self.STATES['GRACE_PERIOD']:
            # Periode tenggang setelah musik berhenti
            if elapsed_time >= self.grace_period_duration:
                self.current_state = self.STATES['RED_LIGHT']
                self.state_start_time = current_time
                
        elif self.current_state == self.STATES['RED_LIGHT']:
            # Dalam status lampu merah, beralih ke lampu hijau setelah durasi tertentu
            if elapsed_time >= self.red_light_duration:
                self.current_state = self.STATES['GREEN_LIGHT']
                self.state_start_time = current_time
                # Cukup mulai musik untuk setiap status lampu hijau
                self.audio_manager.start_music()
    
    def check_violations(self, eyes_open):
        """Memeriksa pelanggaran aturan berdasarkan status permainan"""
        # Selama lampu merah, mata terbuka adalah pelanggaran
        if self.current_state == self.STATES['RED_LIGHT'] and eyes_open:
            print("Pelanggaran terdeteksi! Mata terbuka saat lampu merah.")
            self.current_state = self.STATES['GAME_OVER']
            return True
        return False
    
    def check_win_condition(self):
        """Memeriksa apakah pemain telah mencapai garis finish"""
        if self.player_position >= self.finish_line:
            print("Pemain telah mencapai garis finish! KEMENANGAN!")
            self.current_state = self.STATES['WIN']
            self.audio_manager.play_win_sound()
            return True
        return False
    
    def update_player_position(self, eyes_open):
        """Memperbarui posisi pemain berdasarkan keadaan mata"""
        # Bergerak maju jika mata terbuka selama GREEN_LIGHT
        if self.current_state == self.STATES['GREEN_LIGHT'] and eyes_open:
            self.player_position += self.movement_speed
            # Batasi posisi pemain pada garis finish
            self.player_position = min(self.player_position, self.finish_line)
    
    def reset(self):
        """Mengatur ulang status permainan ke nilai awal"""
        self.current_state = self.STATES['WAITING']
        self.state_start_time = time.time()
        self.player_position = 0
