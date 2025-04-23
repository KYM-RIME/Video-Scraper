import os, re, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal
class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    def __init__(self, urls, output_dir, retries=3, max_workers=5):
        super().__init__()
        self.urls = urls
        self.output_dir = output_dir
        self.retries = retries
        self.max_workers = max_workers
        self.failed_urls = []
    def run(self):
        self.log.emit("Start the download task ...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.download_file, url) for url in self.urls]
            completed = 0
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    self.log.emit(f"The task failed to be executed: {e}")
                completed += 1
                self.progress.emit(int(completed / len(self.urls) * 100))
        if self.failed_urls:
            self.log.emit(f"The download is complete,\nbut {len(self.failed_urls)} file(s) failed to download.")
        else:
            self.log.emit("All files were downloaded successfully!")
    def download_file(self, url):
        filename = os.path.basename(url)
        filepath = os.path.join(self.output_dir, filename)
        for attempt in range(self.retries):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    self.log.emit(f"Successful Download: {url}")
                    return
                else:
                    raise Exception(f"HTTP error: {response.status_code}")
            except Exception as e:
                self.log.emit(f"Try {attempt + 1}/{self.retries} Download Failure: {url} - {e}")
        self.failed_urls.append(url)
class TsMkvApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #fff;
                font-size: 16px;
            }
            QPushButton, QLineEdit, QTextEdit, QRadioButton {
                background-color: #555;
                color: #fff;
                font-size: 16px;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-size: 16px;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                width: 10px;
                margin: 1px;
            }
        """)
    def init_ui(self):
        self.setWindowTitle("Video-Scraper")
        main_layout = QVBoxLayout()
        link_header = QHBoxLayout()
        link_header.addWidget(QLabel(" Link URL:"))
        link_header.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.link_url_paste_button = QPushButton("Paste")
        self.link_url_clear_button = QPushButton("Clear")
        link_header.addWidget(self.link_url_paste_button)
        link_header.addWidget(self.link_url_clear_button)
        self.link_url_input = QLineEdit()
        main_layout.addLayout(link_header)
        main_layout.addWidget(self.link_url_input)
        i3u8_header = QHBoxLayout()
        i3u8_header.addWidget(QLabel(" '*.i3u8' Content:"))
        i3u8_header.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.i3u8_paste_button = QPushButton("Paste")
        self.i3u8_clear_button = QPushButton("Clear")
        i3u8_header.addWidget(self.i3u8_paste_button)
        i3u8_header.addWidget(self.i3u8_clear_button)
        self.i3u8_input = QTextEdit()
        main_layout.addLayout(i3u8_header)
        main_layout.addWidget(self.i3u8_input)
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel(" ThreadPool Executor:"))
        self.thread_pool_input = QLineEdit("10")
        thread_layout.addWidget(self.thread_pool_input)
        main_layout.addLayout(thread_layout)
        save_format_layout = QHBoxLayout()
        save_format_layout.addWidget(QLabel(" Save Format:"))
        self.mkv_radio = QRadioButton("'*.mkv'")
        self.ts_radio = QRadioButton("'*.ts'")
        self.mkv_radio.setChecked(True)
        format_group = QButtonGroup(self)
        format_group.addButton(self.mkv_radio)
        format_group.addButton(self.ts_radio)
        save_format_layout.addWidget(self.mkv_radio)
        save_format_layout.addWidget(self.ts_radio)
        save_format_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(save_format_layout)
        self.start_button = QPushButton("Start")
        main_layout.addWidget(self.start_button)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                width: 10px;
                margin: 1px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        self.link_url_paste_button.clicked.connect(lambda: self.link_url_input.paste())
        self.link_url_clear_button.clicked.connect(self.link_url_input.clear)
        self.i3u8_paste_button.clicked.connect(lambda: self.i3u8_input.paste())
        self.i3u8_clear_button.clicked.connect(self.i3u8_input.clear)
        self.start_button.clicked.connect(self.start_process)
        self.setLayout(main_layout)
        self.resize(800, 600)
    def validate_inputs(self):
        url = self.link_url_input.text().strip()
        i3u8_content = self.i3u8_input.toPlainText().strip()
        thread_count = self.thread_pool_input.text().strip()
        if not re.match(r"^https?://.*?/$", url):
            self.log("Error: [Link URL] format is incorrect.\n - Input example: https://www.example.com/ts/")
            return False
        if not re.findall(r"\.ts\b", i3u8_content):
            self.log("Error: ['*.i3u8' Content] does not contain any '*.ts' files.\n - Input example: 00000.ts 00001.ts 00002.ts ...")
            return False
        if not thread_count.isdigit() or int(thread_count) <= 0:
            self.log("Error: [ThreadPool Executor] must be a positive integer.\n - Input example: 10")
            return False
        return True
    def start_process(self):
        if not self.validate_inputs():
            return
        url = self.link_url_input.text().strip()
        i3u8_content = self.i3u8_input.toPlainText().strip()
        thread_count = int(self.thread_pool_input.text().strip())
        save_format = "mkv" if self.mkv_radio.isChecked() else "ts"
        ts_files = re.findall(r"\b[\w-]+\.ts\b", i3u8_content)
        base_url = url.rsplit("/", 1)[0] + "/"
        download_urls = [base_url + ts for ts in ts_files]
        timestamp = int(time.time())
        output_dir = f"ts-mkv_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        self.log(f"Output Directory: {output_dir}")
        self.worker = DownloadWorker(download_urls, output_dir, max_workers=thread_count)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.log)
        self.worker.finished.connect(lambda: self.on_download_complete(output_dir, save_format))
        self.worker.start()
    def on_download_complete(self, output_dir, save_format):
        self.log("Download task completed!")
        self.progress_bar.setValue(100)
        if save_format == "mkv":
            self.merge_ts_to_mkv(output_dir)
    def merge_ts_to_mkv(self, output_dir):
        self.log("Starting to merge '*.ts' files into '*.mkv' ...")
        ts_files = sorted([f for f in os.listdir(output_dir) if f.endswith(".ts")])
        timestamp = int(time.time())
        mkv_file = os.path.join(output_dir, f"mkv_{timestamp}.mkv")
        try:
            with open(mkv_file, "wb") as outfile:
                for ts_file in ts_files:
                    with open(os.path.join(output_dir, ts_file), "rb") as infile:
                        outfile.write(infile.read())
            self.log(f"Merging completed, output file: {mkv_file}")
            for ts_file in ts_files:
                os.remove(os.path.join(output_dir, ts_file))
        except Exception as e:
            self.log(f"Error merging files: {e}")
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    def log(self, message):
        self.log_output.append(message)
    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Reconfirm ~'Video-Scraper'", "Are you sure you want to quit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #333;
            color: #fff;
            font-size: 16px;
        }
        QPushButton, QLineEdit, QTextEdit, QRadioButton {
            background-color: #555;
            color: #fff;
            font-size: 16px;
        }
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
            font-size: 16px;
        }
        QProgressBar::chunk {
            background-color: #4caf50;
            width: 10px;
            margin: 1px;
        }
    """)
    window = TsMkvApp()
    window.show()
    sys.exit(app.exec())