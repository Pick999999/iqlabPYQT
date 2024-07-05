import sys
import math
from PyQt5.QtCore import QTime, QTimer, Qt, QDateTime, QPointF, QPoint
from PyQt5.QtGui import QPainter, QColor, QPolygon, QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QPushButton, QVBoxLayout

class AnalogClock(QWidget):
    
    def __init__(self, parent=None):
        super(AnalogClock, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.setWindowTitle('Analog Clock')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # Update every second

        self.base_timestamp = None
        self.current_timestamp = None

    def paintEvent(self, event):
        side = min(self.width(), self.height())

        if self.current_timestamp:
            datetime = QDateTime.fromSecsSinceEpoch(self.current_timestamp)
            current_time = datetime.time()
        else:
            current_time = QTime.currentTime()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.black)

        hour_hand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -40)])
        minute_hand = QPolygon([QPoint(7, 8), QPoint(-7, 8), QPoint(0, -70)])
        second_hand = QPolygon([QPoint(1, 1), QPoint(-1, 1), QPoint(0, -90)])

        hour_color = QColor(127, 0, 127)
        minute_color = QColor(0, 127, 127, 191)
        second_color = QColor(127, 0, 0, 191)

        painter.save()
        painter.setBrush(hour_color)
        painter.rotate(30.0 * ((current_time.hour() + current_time.minute() / 60.0)))
        painter.drawConvexPolygon(hour_hand)
        painter.restore()

        painter.save()
        painter.setBrush(minute_color)
        painter.rotate(6.0 * (current_time.minute() + current_time.second() / 60.0))
        painter.drawConvexPolygon(minute_hand)
        painter.restore()

        painter.save()
        painter.setBrush(second_color)
        painter.rotate(6.0 * current_time.second())
        painter.drawConvexPolygon(second_hand)
        painter.restore()

        painter.setPen(hour_color)

        for i in range(0, 12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        painter.setPen(minute_color)

        for j in range(0, 60):
            if (j % 5) != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        # Draw hour numbers
        painter.setPen(Qt.black)
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        for hour in range(1, 13):
            angle = 30 * hour
            x = 70 * math.cos(math.radians(angle - 90))
            y = 70 * math.sin(math.radians(angle - 90))
            painter.drawText(QPointF(x - 5, y + 5), str(hour))

    def update(self):
        if self.base_timestamp:
            self.current_timestamp = self.base_timestamp + (QDateTime.currentSecsSinceEpoch() - self.start_timestamp)
        super().update()

    def update_time(self, timestamp):
        self.base_timestamp = timestamp
        self.start_timestamp = QDateTime.currentSecsSinceEpoch()
        self.current_timestamp = self.base_timestamp

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Analog Clock with Button')
        self.setGeometry(100, 100, 300, 300)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.clock = AnalogClock(self.central_widget)

        self.button = QPushButton("Set Timestamp", self.central_widget)
        self.button.clicked.connect(self.set_timestamp)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.clock)
        self.layout.addWidget(self.button)

    def set_timestamp(self):
        timestamp = 1652918400  # ตัวอย่าง timestamp
        self.clock.update_time(timestamp)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
