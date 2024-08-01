import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QLineEdit, QLabel, QFileDialog
from PyQt5.QtGui import QIcon
from pytube import YouTube
from pydub import AudioSegment


# Nastavení logování
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Funkce pro stažení audia z YouTube
def download_audio(url, output_path):
    try:
        logging.info(f"Starting download for URL: {url}")
        yt = YouTube(url)
        logging.info(f"Title: {yt.title}, Length: {yt.length} seconds")
        audio_stream = yt.streams.filter(only_audio=True).first()
        output_file = audio_stream.download(output_path)
        base, ext = os.path.splitext(output_file)
        new_file = base + '.mp3'
        os.rename(output_file, new_file)
        logging.info(f"Downloaded and saved to: {new_file}")
        return new_file
        logging.info(f"Audio edited and saved to: {output_file}")
    except Exception as e:
        logging.error(f"Error editing audio: {e}")
        logging.error(f"Error downloading audio: {e}")
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None


# Funkce pro úpravu audia
def edit_audio(file_path, start_time, end_time, output_file):
    try:
        audio = AudioSegment.from_file(file_path)
        edited_audio = audio[start_time:end_time]
        edited_audio = edited_audio.fade_in(2000).fade_out(2000)
        edited_audio.export(output_file, format='mp3')
    except Exception as e:
        print(f"Error editing audio: {e}")


# Hlavní třída aplikace
class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Nastavení okna
        self.setWindowTitle('DrumApp')
        self.setGeometry(100, 100, 400, 300)

        # Nastavení ikony aplikace
        self.setWindowIcon(QIcon("MyApp.iconset/icon_64x64.png"))

        # Vytvoření GUI komponent
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Vložte YouTube URL")

        self.download_button = QPushButton('Stáhnout a Upravit', self)
        self.download_button.clicked.connect(self.download_and_edit)

        self.status_label = QLabel('', self)

        # Nastavení layoutu
        layout = QVBoxLayout()
        layout.addWidget(self.url_input)
        layout.addWidget(self.download_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def download_and_edit(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Prosím, vložte platné YouTube URL.")
            return

        logging.info(f"Downloading and editing audio for URL: {url}")
        download_path = "downloads"
        edited_path = "edited"
        os.makedirs(download_path, exist_ok=True)
        os.makedirs(edited_path, exist_ok=True)

        downloaded_file = download_audio(url, download_path)
        if downloaded_file:
            start_time = 10 * 1000  # 10 sekund
            end_time = 30 * 1000  # 30 sekund
            output_file = os.path.join(edited_path, "edited_audio.mp3")
            edit_audio(downloaded_file, start_time, end_time, output_file)
            self.status_label.setText("Audio bylo úspěšně staženo a upraveno!")
            logging.info("Audio successfully downloaded and edited.")
        else:
            logging.error("Download failed.")
            self.status_label.setText("Stažení se nezdařilo.")


# Hlavní část programu
def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
