import logging
import os
import sys
from urllib.error import HTTPError, URLError

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QLineEdit, QLabel, QFileDialog, QProgressBar
from pydub import AudioSegment
import youtube_dl

# Logging settings
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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
        'progress_hooks': [lambda d: progress_callback(int(d['downloaded_bytes'] / d['total_bytes'] * 100)) if progress_callback and d['status'] == 'downloading' else None],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            info_dict = ydl.extract_info(url, download=False)
            file_name = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
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


# Main application class
class MyApp(QWidget):
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
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            QPushButton {
                padding: 10px;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QLabel {
                margin-bottom: 10px;
            }
        """)
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Vložte YouTube URL")

        self.download_button = QPushButton('Stáhnout a Upravit', self)
        self.download_button.clicked.connect(self.download_and_edit)

        self.status_label = QLabel('', self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        # Layout settings
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(self.url_input)
        layout.addWidget(self.download_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def download_and_edit(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Prosím, vložte platné YouTube URL.")
            return

        if not ("youtube.com/watch?v=" in url or "youtu.be/" in url):
            self.status_label.setText("Neplatné YouTube URL.")
            logging.error(f"Invalid YouTube URL: {url}")
            return

        logging.info(f"Downloading and editing audio for URL: {url}")
        download_path = os.path.expanduser("~/Downloads")
        os.makedirs(download_path, exist_ok=True)

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        downloaded_file = download_audio(url, download_path, self.progress_bar.setValue)
        if downloaded_file:
            start_time = 10 * 1000  # 10 seconds
            end_time = 30 * 1000  # 30 seconds
            save_path = os.path.join(download_path, "edited_audio.mp3")
            edit_audio(downloaded_file, start_time, end_time, save_path)
            self.status_label.setText("Audio bylo úspěšně staženo a upraveno!")
            logging.info("Audio successfully downloaded and edited.")
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(False)
            logging.error("Download failed.")
            self.status_label.setText("Stažení se nezdařilo.")


# Main part of the program
def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
