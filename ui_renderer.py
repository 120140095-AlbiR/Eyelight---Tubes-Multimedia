# filepath: c:\Users\4lb17\Documents\buat kuliah\Sistem teknologi multimedia\tubes\Eyelight test 1\ui_renderer.py
import pygame
import time

class UIRenderer:
    def __init__(self, screen, game_state_manager):
        self.screen = screen
        self.gsm = game_state_manager
        
        # Pengaturan font
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Memuat gambar latar belakang
        self.background = pygame.image.load('assets/image/background.png')
        screen_size = screen.get_size()
        self.background = pygame.transform.scale(self.background, screen_size)
        
    def draw_game_elements(self, webcam_surface=None, eyes_open=False, left_ear=0, right_ear=0):
        """Menggambar semua elemen permainan pada layar Pygame"""
        # Gambar latar belakang terlebih dahulu
        self.screen.blit(self.background, (0, 0))
        
        # Menampilkan feed webcam dengan transparansi
        if webcam_surface is not None:
            # Menskalakan feed webcam ke ukuran lebih kecil dan menempatkannya di sudut
            screen_width, screen_height = self.screen.get_size()
            webcam_width = screen_width // 3
            webcam_height = screen_height // 3
            webcam_surface = pygame.transform.scale(webcam_surface, (webcam_width, webcam_height))
            
            # Membuat permukaan transparan
            webcam_alpha = pygame.Surface((webcam_width, webcam_height), pygame.SRCALPHA)
            webcam_alpha.fill((255, 255, 255, 150))  # Putih semi-transparan
            
            # Menerapkan transparansi dan menempatkan ke layar
            webcam_surface.blit(webcam_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(webcam_surface, (screen_width - webcam_width - 10, 10))
        
        # Menggambar pemain dan progres
        self.draw_player_and_progress()
        
        # Tampilan metrik mata
        eye_metrics = f"Left EAR: {left_ear:.2f}, Right EAR: {right_ear:.2f}"
        eye_metrics_text = self.font_small.render(eye_metrics, True, (255, 255, 255))
        self.screen.blit(eye_metrics_text, (10, 50))
        
        # Tampilan status mata
        eye_state = "Mata: TERBUKA" if eyes_open else "Mata: TERTUTUP"
        eye_state_color = (0, 255, 0) if eyes_open else (255, 0, 0)
        eye_state_text = self.font_medium.render(eye_state, True, eye_state_color)
        self.screen.blit(eye_state_text, (10, 10))
        
        # Menggambar overlay status permainan
        self.draw_game_state_overlay(eyes_open)
        
        # Memperbarui tampilan
        pygame.display.flip()
    
    def draw_player_and_progress(self):
        """Menggambar karakter pemain dan bar kemajuan"""
        # Menghitung posisi visual pemain berdasarkan kemajuan mereka
        progress_percent = self.gsm.player_position / self.gsm.finish_line
        
        screen_width, screen_height = self.screen.get_size()
        
        # Dimensi dan posisi bar kemajuan
        bar_width = screen_width - 100
        bar_height = 20
        bar_x = 50
        bar_y = screen_height - 50
        
        # Menggambar bar kemajuan kosong
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        
        # Menggambar bagian terisi dari bar kemajuan
        filled_width = int(bar_width * progress_percent)
        pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, filled_width, bar_height))
        
        # Menggambar batas sekitar bar kemajuan
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Menggambar karakter pemain
        player_x = int(bar_x + (bar_width * progress_percent) - 10)
        player_y = bar_y - 40
        
        # Karakter pemain sederhana (lingkaran dengan mata)
        pygame.draw.circle(self.screen, (255, 255, 0), (player_x, player_y), 20)
        
        # Menambahkan teks persentase di atas bar kemajuan
        percent_text = f"{int(progress_percent * 100)}%"
        text_surf = self.font_medium.render(percent_text, True, (255, 255, 255))
        self.screen.blit(text_surf, (bar_x + bar_width // 2 - text_surf.get_width() // 2, bar_y - 30))
    
    def draw_game_state_overlay(self, eyes_open):
        """Menggambar informasi status permainan dan overlay"""
        screen_width, screen_height = self.screen.get_size()
        
        if self.gsm.current_state == self.gsm.STATES['WAITING']:
            # Status menunggu - menampilkan hitung mundur
            elapsed_time = time.time() - self.gsm.state_start_time
            countdown = max(0, int(self.gsm.countdown_duration - elapsed_time))
            state_text = f"BERSIAP! Mulai dalam {countdown}..."
            
            # Overlay semi-transparan
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Hitam dengan alpha
            self.screen.blit(overlay, (0, 0))
            
            # Menampilkan hitung mundur
            text_surface = self.font_large.render(state_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (screen_width // 2 - text_surface.get_width() // 2, 
                                            screen_height // 2 - text_surface.get_height() // 2))
            
        elif self.gsm.current_state == self.gsm.STATES['GREEN_LIGHT']:
            # Status lampu hijau
            state_text = "LAMPU HIJAU!"
            instruction_text = "(Buka mata Anda untuk bergerak)"
            
            # Overlay hijau semi-transparan jika mata terbuka
            if eyes_open:
                overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                overlay.fill((0, 255, 0, 50))  # Hijau dengan alpha
                self.screen.blit(overlay, (0, 0))
            
            # Menampilkan status dan timer
            text_surface = self.font_large.render(state_text, True, (0, 255, 0))
            self.screen.blit(text_surface, (20, 150))
            
            text_surface = self.font_medium.render(instruction_text, True, (200, 255, 200))
            self.screen.blit(text_surface, (20, 200))
            
            # Menampilkan indikator musik sedang diputar
            if self.gsm.audio_manager.is_playing:
                music_text = "♪ Musik Diputar ♪"
                music_surface = self.font_medium.render(music_text, True, (0, 255, 255))
                self.screen.blit(music_surface, (20, 250))
            
        elif self.gsm.current_state == self.gsm.STATES['GRACE_PERIOD']:
            # Status periode tenggang
            state_text = "MUSIK BERHENTI!"
            instruction_text = "Tutup mata Anda SEKARANG! (periode tenggang 1 detik)"
            
            # Overlay kuning semi-transparan
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 100))  # Kuning dengan alpha
            self.screen.blit(overlay, (0, 0))
            
            # Menampilkan status dan timer
            text_surface = self.font_large.render(state_text, True, (255, 255, 0))
            self.screen.blit(text_surface, (screen_width // 2 - text_surface.get_width() // 2, 
                                            screen_height // 3))
            
            text_surface = self.font_medium.render(instruction_text, True, (255, 255, 0))
            self.screen.blit(text_surface, (screen_width // 2 - text_surface.get_width() // 2, 
                                            screen_height // 3 + 60))
            
            # Menampilkan hitung mundur periode tenggang
            elapsed_time = time.time() - self.gsm.state_start_time
            remaining = max(0, self.gsm.grace_period_duration - elapsed_time)
            timer_text = f"Waktu tersisa: {remaining:.1f}d"
            timer_surface = self.font_medium.render(timer_text, True, (255, 255, 0))
            self.screen.blit(timer_surface, (screen_width // 2 - timer_surface.get_width() // 2, 
                                             screen_height // 3 + 120))
            
        elif self.gsm.current_state == self.gsm.STATES['RED_LIGHT']:
            # Status lampu merah
            state_text = "LAMPU MERAH!"
            instruction_text = "(Tetap tutup mata Anda!)"
            
            # Overlay merah semi-transparan jika mata terbuka (pelanggaran)
            if eyes_open:
                overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 80))  # Merah dengan alpha
                self.screen.blit(overlay, (0, 0))
            
            # Menampilkan status dan timer
            text_surface = self.font_large.render(state_text, True, (255, 0, 0))
            self.screen.blit(text_surface, (20, 150))
            
            text_surface = self.font_medium.render(instruction_text, True, (255, 200, 200))
            self.screen.blit(text_surface, (20, 200))
            
            # Tampilan timer
            elapsed_time = time.time() - self.gsm.state_start_time
            remaining = max(0, self.gsm.red_light_duration - elapsed_time)
            timer_text = f"Waktu: {remaining:.1f}d"
            timer_surface = self.font_medium.render(timer_text, True, (255, 0, 0))
            self.screen.blit(timer_surface, (20, 250))
            
        elif self.gsm.current_state == self.gsm.STATES['GAME_OVER']:
            # Status permainan berakhir
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((100, 0, 0, 180))  # Merah dengan alpha
            self.screen.blit(overlay, (0, 0))
            
            # Menampilkan teks permainan berakhir
            state_text = "PERMAINAN BERAKHIR!"
            text_surface = self.font_large.render(state_text, True, (255, 0, 0))
            self.screen.blit(text_surface, (screen_width // 2 - text_surface.get_width() // 2, 
                                            screen_height // 2 - text_surface.get_height() // 2 - 50))
            
            # Menampilkan instruksi restart
            instructions = "Tekan SPASI untuk memulai ulang permainan"
            instructions_text = self.font_medium.render(instructions, True, (255, 255, 255))
            self.screen.blit(instructions_text, (screen_width // 2 - instructions_text.get_width() // 2, 
                                                 screen_height // 2 + 50))
                                                
        elif self.gsm.current_state == self.gsm.STATES['WIN']:
            # Status menang
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 100, 0, 180))  # Hijau dengan alpha
            self.screen.blit(overlay, (0, 0))
            
            # Menampilkan teks kemenangan
            state_text = "ANDA MENANG!"
            text_surface = self.font_large.render(state_text, True, (0, 255, 0))
            self.screen.blit(text_surface, (screen_width // 2 - text_surface.get_width() // 2, 
                                            screen_height // 2 - text_surface.get_height() // 2 - 50))
            
            # Menampilkan instruksi restart
            instructions = "Tekan SPASI untuk bermain lagi"
            instructions_text = self.font_medium.render(instructions, True, (255, 255, 255))
            self.screen.blit(instructions_text, (screen_width // 2 - instructions_text.get_width() // 2, 
                                                 screen_height // 2 + 50))
