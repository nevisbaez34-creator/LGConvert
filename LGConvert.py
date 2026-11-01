import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QProgressBar, QTextEdit, QFileDialog
)
from PyQt5.QtCore import pyqtSignal, QObject, Qt
import yt_dlp


class DownloadWorker(QObject):
    progress_signal = pyqtSignal(dict)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, url, download_type, save_path, ffmpeg_path):
        super().__init__()
        self.url = url
        self.download_type = download_type
        self.save_path = save_path
        self.ffmpeg_path = ffmpeg_path

    def run(self):
        def progress_hook(d):
            if d['status'] == 'downloading':
                self.progress_signal.emit(d)
            elif d['status'] == 'finished':
                self.log_signal.emit("[SISTEMA] Descarga completada. Procesando formato final con FFmpeg...")

        # Configuración base de yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
        }

        # Si FFmpeg está empaquetado de forma interna, se lo asignamos
        if self.ffmpeg_path:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_path

        # Mapeo de formatos modernos y optimizados
        if self.download_type == 'Audio (.aac puro)':
            ydl_opts.update({
                'format': 'bestaudio/best', 
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio', 
                    'preferredcodec': 'm4a', 
                }]
            })
        elif self.download_type == 'Audio (.m4a AAC)':
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a', 'preferredquality': '192'}]})
        elif self.download_type == 'Audio (.opus)':
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'opus', 'preferredquality': '192'}]})
        elif self.download_type == 'Audio (.mp3)':
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]})
        elif self.download_type == 'Audio (.wav)':
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav', 'preferredquality': '192'}]})
        elif self.download_type == 'Audio (.flac)':
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'flac', 'preferredquality': '192'}]})
        elif self.download_type == 'Audio (.ogg Vorbis)':
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'vorbis', 'preferredquality': '192'}]})
        elif self.download_type == 'Audio (ALAC Lossless)':
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'alac'}]})
        elif self.download_type == 'Audio Ringtone (.m4r)':
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}]})
        elif self.download_type == 'Video (.mp4 AVC/H264)':
            ydl_opts.update({'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'merge_output_format': 'mp4'})
        elif self.download_type == 'Video (.mp4 AV1/Modern)':
            ydl_opts.update({'format': 'bestvideo[vcodec^=av01]+bestaudio/best', 'merge_output_format': 'mp4'})
        elif self.download_type == 'Video (.webm VP9/Opus)':
            ydl_opts.update({'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best', 'merge_output_format': 'webm'})
        elif self.download_type == 'Video (.mkv Matroska)':
            ydl_opts.update({'format': 'bestvideo+bestaudio/best', 'merge_output_format': 'mkv'})

        try:
            self.log_signal.emit(f"[INICIO] Analizando enlace: {self.url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                
                filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(filename)

                # Post-procesamiento de extensiones especiales (.aac puro y .m4r)
                if self.download_type == 'Audio (.aac puro)':
                    m4a_path = base + ".m4a"
                    aac_path = base + ".aac"
                    if os.path.exists(m4a_path):
                        ffmpeg_cmd = self.ffmpeg_path if self.ffmpeg_path else 'ffmpeg'
                        subprocess.run([ffmpeg_cmd, '-y', '-i', m4a_path, '-acodec', 'copy', aac_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        try:
                            os.remove(m4a_path)
                        except:
                            pass

                elif self.download_type == 'Audio Ringtone (.m4r)':
                    m4a_path = base + ".m4a"
                    m4r_path = base + ".m4r"
                    if os.path.exists(m4a_path):
                        os.rename(m4a_path, m4r_path)

            self.finished_signal.emit(True, "Descarga y conversión completadas con éxito.")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class LGConvertWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("LGConvert 4 (Python 3.15.2)")
        self.resize(680, 520)
        self.setStyleSheet("""
            QWidget { background-color: #050505; color: #00ff66; font-family: 'Consolas', 'Courier New', monospace; }
            QLabel { font-size: 13px; font-weight: bold; color: #ff6b00; }
            QLineEdit, QComboBox { background-color: #0a0a0a; border: 1px solid #1a3d24; border-radius: 4px; padding: 6px; color: #00ff66; font-size: 12px; }
            QPushButton { background-color: #112215; border: 1px solid #00ff66; color: #00ff66; padding: 8px 14px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #00ff66; color: #000000; }
            QProgressBar { border: 1px solid #1a3d24; border-radius: 4px; text-align: center; background-color: #0a0a0a; color: #ffffff; }
            QProgressBar::chunk { background-color: #ff6b00; }
            QTextEdit { background-color: #080808; border: 1px solid #113318; border-radius: 4px; color: #00ff66; font-size: 11px; }
        """)

        layout = QVBoxLayout()

        title_label = QLabel("=== LGCONVERT 4 - MEDIA DOWNLOADER HUB ===")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Botón de auto-actualización de yt-dlp
        update_layout = QHBoxLayout()
        self.btn_update_ytdlp = QPushButton("Actualizar yt-dlp Online")
        self.btn_update_ytdlp.clicked.connect(self.update_ytdlp_engine)
        update_layout.addWidget(self.btn_update_ytdlp)
        layout.addLayout(update_layout)

        layout.addWidget(QLabel("URL del Video / Stream:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Pega aquí el enlace de YouTube, TikTok, etc...")
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel("Formato de Salida:"))
        self.format_box = QComboBox()
        self.format_box.addItems([
            "Audio (.aac puro)",
            "Audio (.m4a AAC)",
            "Audio (.opus)",
            "Audio (.mp3)",
            "Audio (.wav)",
            "Audio (.flac)",
            "Audio (.ogg Vorbis)",
            "Audio (ALAC Lossless)",
            "Audio Ringtone (.m4r)",
            "Video (.mp4 AVC/H264)",
            "Video (.mp4 AV1/Modern)",
            "Video (.webm VP9/Opus)",
            "Video (.mkv Matroska)"
        ])
        layout.addWidget(self.format_box)

        layout.addWidget(QLabel("Carpeta de Destino:"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(os.path.expanduser("~/Downloads"))
        self.btn_browse = QPushButton("Explorar")
        self.btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.btn_browse)
        layout.addLayout(path_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.btn_download = QPushButton("Descargar")
        self.btn_download.clicked.connect(self.start_download)
        layout.addWidget(self.btn_download)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", self.path_input.text())
        if folder:
            self.path_input.setText(folder)

    def log(self, text):
        self.log_area.append(text)

    def update_ytdlp_engine(self):
        self.log("[SISTEMA] Comprobando actualizaciones de yt-dlp...")
        def run_update():
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
                self.log("[ÉXITO] yt-dlp se ha actualizado a la última versión disponible.")
            except Exception as e:
                self.log(f"[ERROR] No se pudo actualizar yt-dlp: {e}")
        threading.Thread(target=run_update, daemon=True).start()

    def get_ffmpeg_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            ffmpeg_bin = os.path.join(base_path, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_bin):
                return ffmpeg_bin
        return None

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.log("[ERROR] Ingresa una URL válida.")
            return

        save_path = self.path_input.text().strip()
        if not os.path.exists(save_path):
            self.log("[ERROR] La carpeta de destino no es válida.")
            return

        download_type = self.format_box.currentText()
        ffmpeg_path = self.get_ffmpeg_path()

        self.btn_download.setEnabled(False)
        self.progress_bar.setValue(0)

        self.thread = threading.Thread(
            target=self.run_worker, 
            args=(url, download_type, save_path, ffmpeg_path)
        )
        self.thread.daemon = True
        self.thread.start()

    def run_worker(self, url, download_type, save_path, ffmpeg_path):
        worker = DownloadWorker(url, download_type, save_path, ffmpeg_path)
        worker.progress_signal.connect(lambda d: self.progress_bar.setValue(int((d.get('downloaded_bytes', 0) / (d.get('total_bytes') or d.get('total_bytes_estimate', 1)) * 100)) if (d.get('total_bytes') or d.get('total_bytes_estimate', 0)) > 0 else 0))
        worker.log_signal.connect(self.log)
        worker.finished_signal.connect(lambda s, m: (self.btn_download.setEnabled(True), self.progress_bar.setValue(100) if s else None, self.log(f"[{'ÉXITO' if s else 'ERROR'}] {m}")))
        worker.run()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LGConvertWindow()
    window.show()
    sys.exit(app.exec_())
