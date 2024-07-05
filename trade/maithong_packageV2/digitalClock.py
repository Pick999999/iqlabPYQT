import sys
from PyQt5.QtCore import QTimer, QDateTime, QLocale, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton

class DigitalClock(QWidget):
    def __init__(self, parent=None):
        super(DigitalClock, self).__init__(parent)
        self.setMinimumSize(200, 100)
        self.setWindowTitle('Digital Clock')

        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: green; font-size: 48px;")

        font = QFont("Courier", 48, QFont.Bold)
        self.time_label.setFont(font)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.time_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

        self.base_timestamp = None
        self.current_timestamp = None

    def update_time(self):
        if self.base_timestamp:
            self.current_timestamp = self.base_timestamp + (QDateTime.currentSecsSinceEpoch() - self.start_timestamp)
            datetime = QDateTime.fromSecsSinceEpoch(self.current_timestamp)
            current_time = datetime.time()
        else:
            current_time = QDateTime.currentDateTime().time()

        self.time_label.setText(current_time.toString("hh:mm:ss"))

    def set_time(self, timestamp):
        self.base_timestamp = timestamp
        self.start_timestamp = QDateTime.currentSecsSinceEpoch()
        self.current_timestamp = self.base_timestamp
        self.update_time()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Digital Clock with Button')
        self.setGeometry(100, 100, 300, 200)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.clock = DigitalClock(self.central_widget)

        self.button = QPushButton("Set Timestamp", self.central_widget)
        self.button.clicked.connect(self.set_timestamp)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.clock)
        self.layout.addWidget(self.button)

    def set_timestamp(self):
        timestamp = 1652918400  # ตัวอย่าง timestamp
        self.clock.set_time(timestamp)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set QLocale to English
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
