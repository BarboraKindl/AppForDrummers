import logging
import os
import sys

import youtube_dl
import yt_dlp as youtube_dl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QLineEdit, QLabel, QFileDialog, QProgressBar
from pydub import AudioSegment

# Logging settings
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_save_path(file_path=None):
    download_path = os.path.expanduser("~/Downloads")
    os.makedirs(download_path, exist_ok=True)
    if file_path:
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        return os.path.join(download_path, f"{name}_drumless{ext}")
    return download_path


# Function to download audio from YouTube
def download_audio(url, output_path, progress_callback=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [lambda d: progress_callback(int(
            d['downloaded_bytes'] / d[
                'total_bytes'] * 100)) if progress_callback and d[
            'status'] == 'downloading' else None],
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info_dict = ydl.extract_info(url, download=False)
            file_name = ydl.prepare_filename(info_dict).replace('.webm',
                                                                '.mp3').replace(
                '.m4a', '.mp3')
            logging.info(f"Downloaded and saved to: {file_name}")
            return file_name
    except Exception as e:
        logging.error(f"Error downloading audio: {e}", exc_info=True)
        return None


# Function to edit audio
def edit_audio(file_path, start_time, end_time, output_file):
    try:
        audio = AudioSegment.from_file(file_path)
        edited_audio = audio[start_time:end_time]
        edited_audio = edited_audio.fade_in(2000).fade_out(2000)
        edited_audio.export(output_file, format='mp3')
    except Exception as e:
        print(f"Error editing audio: {e}")


class MyApp(QWidget):
    def select_and_edit_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Vyberte MP3 soubor",
                                                   "",
                                                   "MP3 Files (*.mp3);;All Files (*)",
                                                   options=options)
        if file_path:
            logging.info(f"Selected file: {file_path}")
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            self.status_label.setText("Soubor byl úspěšně vybrán!")
        else:
            self.status_label.setText("Výběr souboru byl zrušen.")
            logging.info("File selection was canceled.")

    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle('DrumApp')
        self.setGeometry(100, 100, 400, 300)

        # Application icon settings
        self.setWindowIcon(QIcon("MyApp.iconset/icon_64x64.png"))

        # Set stylesheet for the application
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #ecf0f1;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #34495e;
                border-radius: 5px;
                margin-bottom: 10px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            QPushButton {
                padding: 10px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QLabel {
                margin-bottom: 10px;
            }
            QProgressBar {
                background-color: #34495e;
                border: 1px solid #34495e;
                border-radius: 5px;
                text-align: center;
                color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
            }
        """)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Vložte YouTube URL")

        self.download_button = QPushButton('Stáhnout mp3', self)
        self.download_button.clicked.connect(self.download_mp3)

        self.download_mp4_button = QPushButton('Stáhnout mp4', self)
        self.download_mp4_button.clicked.connect(self.download_mp4)

        self.select_file_button = QPushButton('Vybrat soubor', self)
        self.select_file_button.clicked.connect(self.select_and_edit_file)

        self.status_label = QLabel('', self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        # Layout settings
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        layout.addWidget(self.url_input)
        layout.addWidget(self.download_button)
        layout.addWidget(self.download_mp4_button)
        layout.addWidget(self.select_file_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def download_mp3(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Prosím, vložte platné YouTube URL.")
            return

        if not ("youtube.com/watch?v=" in url or "youtu.be/" in url):
            self.status_label.setText("Neplatné YouTube URL.")
            logging.error(f"Invalid YouTube URL: {url}")
            return

        logging.info(f"Downloading video for URL: {url}")
        download_path = get_save_path()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        downloaded_file = download_youtube_video(url, download_path)
        if downloaded_file:
            self.status_label.setText("Video bylo úspěšně staženo!")
        else:
            self.status_label.setText("Stažení se nezdařilo.")
        self.progress_bar.setVisible(False)

    def download_mp4(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Prosím, vložte platné YouTube URL.")
            return

        if not ("youtube.com/watch?v=" in url or "youtu.be/" in url):
            self.status_label.setText("Neplatné YouTube URL.")
            logging.error(f"Invalid YouTube URL: {url}")
            return

        logging.info(f"Downloading video for URL: {url}")
        download_path = get_save_path()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        downloaded_file = download_youtube_video(url, download_path)
        if downloaded_file:
            self.status_label.setText("Video bylo úspěšně staženo!")
        else:
            self.status_label.setText("Stažení se nezdařilo.")
        self.progress_bar.setVisible(False)


def download_youtube_video(url, output_path='.'):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: logging.info(f"Stahování: {d['_percent_str']}")],
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info_dict = ydl.extract_info(url, download=False)
            file_name = ydl.prepare_filename(info_dict)
            logging.info(f"Video úspěšně staženo jako '{file_name}' do složky {output_path}")
            return file_name
    except Exception as e:
        logging.error(f"Chyba při stahování videa: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
