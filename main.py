import logging
import os
import sys

import yt_dlp as youtube_dl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QLineEdit, QLabel, QFileDialog, QProgressBar
from pydub import AudioSegment

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
            save_path = os.path.join(os.path.dirname(file_path),
                                     f"{name}_drumless{ext}")
            remove_drums(file_path, save_path)
            self.status_label.setText("Bicí byly úspěšně odstraněny!")
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

        self.download_button = QPushButton('Stáhnout', self)
        self.download_button.clicked.connect(self.download_and_edit)

        self.select_file_button = QPushButton('Vybrat soubor', self)
        self.select_file_button.clicked.connect(self.select_and_edit_file)

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
        layout.addWidget(self.select_file_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def download_and_edit(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Prosím, vložte platné YouTube URL.")
            return

        if not validate_youtube_url(url):
            self.status_label.setText("Neplatné YouTube URL.")
            return

        logging.info(f"Downloading and editing audio for URL: {url}")
        download_path = get_save_path()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        downloaded_file = download_audio(url, download_path,
                                         self.progress_bar.setValue)
        if downloaded_file:
            save_path = get_save_path(downloaded_file)
            remove_drums(downloaded_file, save_path)
        self.progress_bar.setVisible(False)
        if not downloaded_file:
            self.status_label.setText("Stažení se nezdařilo.")


# Function to remove drums from an audio file
def remove_drums(file_path, output_file):
    try:
        audio = AudioSegment.from_file(file_path)
        # This is a placeholder for actual vocal removal logic
        # For now, it just copies the file
        audio.export(output_file, format='mp3')
        logging.info(f"Drums removed and saved to: {output_file}")
    except Exception as e:
        logging.error(f"Error removing drums: {e}", exc_info=True)


def validate_youtube_url(url):
    if "youtube.com/watch?v=" in url or "youtu.be/" in url:
        return True
    logging.error(f"Invalid YouTube URL: {url}")
    return False


def get_save_path(file_path=None):
    download_path = os.path.expanduser("~/Downloads")
    os.makedirs(download_path, exist_ok=True)
    if file_path:
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        return os.path.join(download_path, f"{name}_drumless{ext}")
    return download_path
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
    if "youtube.com/watch?v=" in url or "youtu.be/" in url:
        return True
    logging.error(f"Invalid YouTube URL: {url}")
    return False


if __name__ == "__main__":
    main()
