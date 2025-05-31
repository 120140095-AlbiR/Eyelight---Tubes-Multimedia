import time
import random

class GameStateManager:
    def __init__(self, audio_manager):
        # Mendefinisikan status permainan
        self.STATES = {
            'START_MENU': -1,  
            'WAITING': 0,
            'GREEN_LIGHT': 1,
            'GRACE_PERIOD': 2,
            'RED_LIGHT': 3,
            'GAME_OVER': 4,
            'WIN': 5
        }
        self.current_state = self.STATES['START_MENU']  # Mulai dengan menu awal
        self.state_start_time = time.time()
        
        # Pengaturan waktu permainan (dalam detik)
        self.green_light_duration = 5.0  # Durasi green light (akan diganti oleh musik)
        self.red_light_duration = 3.0    # Durasi red light
        self.countdown_duration = 3.0    # Durasi hitung mundur awal
        self.grace_period_duration = 1.0  # Periode tenggang setelah musik berhenti
        
        # Menyimpan referensi audio manager
        self.audio_manager = audio_manager
          # Opsi menu
        self.menu_options = ["Start Game", "How to Play", "Exit"]
        self.selected_option = 0
        
        # Status tambahan untuk menu cara bermain
        self.STATES['HOW_TO_PLAY'] = -2  # Status menampilkan cara bermain
        
        # Kemajuan pemain
        self.player_position = 0
        self.finish_line = 1000  # Posisi target untuk menang
        self.movement_speed = 2  # Seberapa cepat pemain bergerak ketika mata terbuka
        
    def get_state_name(self, state):
        """Mengkonversi nilai status menjadi nama"""
        for name, value in self.STATES.items():
            if value == state:
                return name
        return "UNKNOWN"
    
    def stop_current_music(self):
        """Paksa menghentikan musik yang sedang diputar dan memicu grace period"""
        if self.current_state == self.STATES['GREEN_LIGHT'] and self.audio_manager.is_playing:
            self.audio_manager.stop_music()
            self.current_state = self.STATES['GRACE_PERIOD']
            self.state_start_time = time.time()
            return True
        return False
    
    def update_state(self, current_time):
        """Memperbarui status permainan berdasarkan timer dan status musik"""
        # Jika di menu awal, tidak perlu memperbarui status permainan
        if self.current_state == self.STATES['START_MENU']:
            return
        
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
            if self.audio_manager.is_playing and random.random() < 0.005:
                print("Musik berhenti secara random saat diputar!")
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
            # Dalam status red light, beralih ke green light setelah durasi tertentu
            if elapsed_time >= self.red_light_duration:
                self.current_state = self.STATES['GREEN_LIGHT']
                self.state_start_time = current_time
                # Mulai musik untuk setiap status green light
                self.audio_manager.start_music()
    
    def check_violations(self, eyes_open):
        """Memeriksa pelanggaran aturan berdasarkan status permainan"""
        # Selama red light, mata terbuka adalah pelanggaran
        if self.current_state == self.STATES['RED_LIGHT'] and eyes_open:
            print("Pelanggaran terdeteksi! Mata terbuka saat red light.")
            self.current_state = self.STATES['GAME_OVER']
            self.audio_manager.play_lose_sound()
            return True
        return False
    
    def check_win_condition(self):
        """Memeriksa apakah pemain telah mencapai garis finish"""
        if self.player_position >= self.finish_line:
            print("Pemain telah mencapai garis finish!")
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
        self.current_state = self.STATES['START_MENU']  # Kembali ke menu awal
        self.state_start_time = time.time()
        self.player_position = 0
        
    def start_game(self):
        """Memulai permainan dari menu awal"""
        self.current_state = self.STATES['WAITING']
        self.state_start_time = time.time()
        self.player_position = 0
    
    def select_menu_option(self, direction):
        """Memilih opsi menu (naik/turun)"""
        if self.current_state == self.STATES['START_MENU']:
            if direction == "up" and self.selected_option > 0:
                self.selected_option -= 1
            elif direction == "down" and self.selected_option < len(self.menu_options) - 1:
                self.selected_option += 1
    def activate_selected_option(self):
        """Mengaktifkan opsi menu yang dipilih"""
        if self.current_state == self.STATES['START_MENU']:
            if self.selected_option == 0:  # Mulai Permainan
                return "start_game"
            elif self.selected_option == 1:  # Cara Bermain
                self.current_state = self.STATES['HOW_TO_PLAY']
                return "how_to_play"
            elif self.selected_option == 2:  # Keluar
                return "exit"
        elif self.current_state == self.STATES['HOW_TO_PLAY']:
            # Kembali ke menu utama ketika tombol ditekan di layar cara bermain
            self.current_state = self.STATES['START_MENU']
            return "back_to_menu"
        return None
