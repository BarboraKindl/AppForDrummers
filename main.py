import logging
import os
import sys
from urllib.error import HTTPError, URLError

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QLineEdit, QLabel, QFileDialog, QProgressBar
from pydub import AudioSegment
from pytube import YouTube

# Logging settings
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Function to download audio from YouTube
def download_audio(url, output_path, progress_callback=None):
    try:
        logging.info(f"Starting download for URL: {url}")
        yt = YouTube(url)
        logging.info(f"Title: {yt.title}, Length: {yt.length} seconds")
        audio_stream = yt.streams.filter(only_audio=True).first()
        total_size = audio_stream.filesize
        bytes_downloaded = 0

        def on_progress(stream, chunk, bytes_remaining):
            nonlocal bytes_downloaded
            bytes_downloaded += len(chunk)
            if progress_callback:
                progress_callback(int(bytes_downloaded / total_size * 100))

        yt.register_on_progress_callback(on_progress)
        output_file = audio_stream.download(output_path)
        base, ext = os.path.splitext(output_file)
        new_file = base + '.mp3'
        os.rename(output_file, new_file)
        logging.info(f"Downloaded and saved to: {new_file}")
        return new_file
    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        if isinstance(e, HTTPError):
            logging.error(f"HTTP Error: {e.code} - {e.reason}")
        elif isinstance(e, URLError):
            logging.error(f"URL Error: {e.reason}")
        else:
            logging.error(f"Unexpected error: {e}")
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

        try:
            yt = YouTube(url)
        except Exception as e:
            self.status_label.setText("Neplatné YouTube URL.")
            logging.error(f"Invalid YouTube URL: {e}")
            return

        logging.info(f"Downloading and editing audio for URL: {url}")
        save_path, _ = QFileDialog.getSaveFileName(self, "Uložit soubor",
                                                   "", "MP3 Files (*.mp3)")
        if save_path:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            download_path = os.path.dirname(save_path)
            os.makedirs(download_path, exist_ok=True)

            downloaded_file = download_audio(url, download_path, self.progress_bar.setValue)
            if downloaded_file:
                start_time = 10 * 1000  # 10 seconds
                end_time = 30 * 1000  # 30 seconds
                edit_audio(downloaded_file, start_time, end_time,
                           save_path)
                self.status_label.setText(
                    "Audio bylo úspěšně staženo a upraveno!")
                logging.info("Audio successfully downloaded and edited.")
                self.progress_bar.setVisible(False)
            else:
                self.progress_bar.setVisible(False)
                logging.error("Download failed.")
                self.status_label.setText("Stažení se nezdařilo.")
        else:
            self.status_label.setText("Uložení bylo zrušeno.")


# Main part of the program
def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
