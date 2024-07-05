import sys,os,time
import math
sys.path.append(os.path.join(os.path.dirname(__file__), 'maithong_packageV2'))
from maithong_packageV2 import pdatetime,mylib,pyqtHelper as pt , broker 

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QGridLayout, QCheckBox, QRadioButton, QLineEdit, QMenuBar, QAction
from PyQt5.QtCore import Qt, QTime, QTimer,QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush,QPolygon,QFont

class AnalogClock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.setMinimumSize(200, 200)
        self.setWindowTitle("Analog Clock")

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        time = QTime.currentTime()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        # Draw the hour hand
        hour_hand = QPolygon([QPoint(6, 8), QPoint(-6, 8), QPoint(0, -40)])
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(127, 0, 127))

        painter.save()
        painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        painter.drawConvexPolygon(hour_hand)
        painter.restore()

        # Draw the minute hand
        minute_hand = QPolygon([QPoint(4, 8), QPoint(-4, 8), QPoint(0, -70)])
        painter.setBrush(QColor(0, 127, 127, 191))

        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(minute_hand)
        painter.restore()

        # Draw the second hand
        second_hand = QPolygon([QPoint(2, 8), QPoint(-2, 8), QPoint(0, -90)])
        painter.setBrush(QColor(255, 0, 0))

        painter.save()
        painter.rotate(6.0 * time.second())
        painter.drawConvexPolygon(second_hand)
        painter.restore()

        # Draw the clock ticks
        painter.setPen(QPen(Qt.black, 1))
        font = QFont("Arial", 8)
        painter.setFont(font)
        for i in range(1, 13):
            angle = math.radians(30 * i)
            x = int(80 * math.cos(angle) - 10)
            y = int(80 * math.sin(angle) - 9)
            txt = i + 3 
            if txt >=13 :
               txt = txt - 12 
            painter.drawText(x, y, 20, 20, Qt.AlignCenter, str(txt) )
             
             
        for i in range(0, 60):
            if (i % 5) == 0:
                painter.drawLine(88, 0, 96, 0)
            else:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pick Trader")
        self.showMaximized()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()
        frame_width = screen_width // 2
        frame_height = int(screen_height * 0.45)

        # Create frames with specified size and position
        self.frameA = self.create_frame_a(frame_width, frame_height)
        self.frameB = self.create_frame_b(frame_width, frame_height)
        self.frameC = self.create_frame_c(frame_width, frame_height)
        self.frameD = self.create_frame_d(frame_width, frame_height)

        # Add frames to layout
        frame_row_1 = QHBoxLayout()
        frame_row_1.addWidget(self.frameA)
        frame_row_1.addWidget(self.frameB)

        frame_row_2 = QHBoxLayout()
        frame_row_2.addWidget(self.frameC)
        frame_row_2.addWidget(self.frameD)

        self.main_layout.addLayout(frame_row_1)
        self.main_layout.addLayout(frame_row_2)

        # Menu bar
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        file_menu = self.menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        self.counter_label = QLabel("Counter: 0", self)
        self.counter_label.setStyleSheet("font-size: 20px; color: white; background-color: black;")
        self.counter_value = 0
        self.statusBar().addPermanentWidget(self.counter_label)

    def create_frame_a(self, width, height):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFixedSize(width, height)
        layout = QVBoxLayout()

        # Caption
        caption = QLabel("Time Trade")
        caption.setAlignment(Qt.AlignCenter)
        layout.addWidget(caption)

        # Analog clock
        self.clock_widget = AnalogClock()
        layout.addWidget(self.clock_widget)

        # Countdown timer
        self.countdown_label = QLabel()
        self.countdown_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.countdown_label)

        self.update_time()
        self.start_timer()

        frame.setLayout(layout)
        return frame

    def create_frame_b(self, width, height):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFixedSize(width, height)
        layout = QVBoxLayout()

        # Caption
        caption = QLabel("Tabs")
        caption.setAlignment(Qt.AlignCenter)
        layout.addWidget(caption)

        # Tabs
        # tabs = QTabWidget()
        # for i in range(1, 4):
        #     tab = QWidget()
        #     tab_layout = QVBoxLayout()
        #     tab_label = QLabel(f"Content of Tab {i}")
        #     tab_layout.addWidget(tab_label)
        #     tab.setLayout(tab_layout)
        #     tabs.addTab(tab, f"Tab {i}")
        tabcaption = ['เลือกคู่เงิน','เลือกเทคนิค','dddd','dfffff']
        tabs = pt.createTab(tabcaption)
        layout.addWidget(tabs)
        
        frame.setLayout(layout)
        return frame

    def create_frame_c(self, width, height):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFixedSize(width, height)
        layout = QVBoxLayout()

        # Caption
        caption = QLabel("Table")
        caption.setAlignment(Qt.AlignCenter)
        layout.addWidget(caption)

        # Table
        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        for row in range(3):
            for column in range(3):
                table.setItem(row, column, QTableWidgetItem(f"Item {row + 1}, {column + 1}"))

        layout.addWidget(table)
        frame.setLayout(layout)
        return frame

    def create_frame_d(self, width, height):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFixedSize(width, height)
        layout = QGridLayout()

        # Caption
        caption = QLabel("Form Elements")
        caption.setAlignment(Qt.AlignCenter)
        layout.addWidget(caption, 0, 0, 1, 2)

        # Checkbox, RadioButton, TextBox, Label
        checkbox = QCheckBox("Checkbox")
        radio = QRadioButton("Radio Button")
        textbox = QLineEdit()
        label = QLabel("Label")

        layout.addWidget(checkbox, 1, 0)
        layout.addWidget(radio, 1, 1)
        layout.addWidget(textbox, 2, 0)
        layout.addWidget(label, 2, 1)

        frame.setLayout(layout)
        return frame

    def update_time(self):
        self.clock_widget.update()
        self.countdown_timer()

    def start_timer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

    def countdown_timer(self):
        current_time = QTime.currentTime()
        second = current_time.second()
        if second == 00 or second == 30:
            self.countdown_value = 30
        elif second < 31:
            self.countdown_value = 29 - second+1
        else:
            self.countdown_value = 59 - second+1
        self.countdown_label.setText(f"Countdown: {self.countdown_value} seconds")

        if self.countdown_value == 0 or self.countdown_value == 30:
            self.counter_value += 1
            self.counter_label.setText(f"Counter: {self.countdown_value}")
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
