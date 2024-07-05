import sys,os 
import broker
# from maithong_packageV2 import pdatetime,mylib,pyqtHelper as pt , broker 

# I_want_money = broker.getIQ()
# broker.IQ_CheckCurpair_OpenedBinary(I_want_money)  

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QGridLayout, QCheckBox, QRadioButton, QLineEdit, QMenuBar, QAction
from PyQt5.QtCore import Qt, QTime, QTimer,QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush,QPolygon,QFont

from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtHelper

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pick Trader")
        self.showMaximized()
        
        self.grid = QGridLayout()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()
        frame_width = screen_width // 2
        frame_height = int(screen_height * 0.45) 
        
        self.setGeometry(0, 0, screen_width ,screen_height)

        # Create frames with specified size and position
        self.frameA = self.create_frame_a(frame_width, frame_height)
        self.frameB = self.create_frame_b(frame_width-20, frame_height)
        self.frameC = self.create_frame_c(frame_width, frame_height-20)
        self.frameD = self.create_frame_d(frame_width-20, frame_height-20)

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

    def add_widget_with_default_alignment(self,widget, row, col):
        
        self.grid.addWidget(widget, row, col, alignment=Qt.AlignTop | Qt.AlignLeft)
            
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
        # self.clock_widget = AnalogClock()
        # layout.addWidget(self.clock_widget)

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
        Gridlayout = QGridLayout()

        # Caption
        caption = QLabel("Form Elements")
        caption.setAlignment(Qt.AlignTop)
        Gridlayout.addWidget(caption, 1, 0, Qt.AlignLeft | Qt.AlignTop)
        # Gridlayout.addWidget(caption,  0, 0, 0, 2)

        # Checkbox, RadioButton, TextBox, Label
        checkboxList = []
        checkboxList.append(QCheckBox("EURUSD"))
        checkboxList.append(QCheckBox("EURGBP"))
        checkboxList.append(QCheckBox("EURJPY"))
        # frame.setGeometry(QtCore.QRect(16, 12, 635, 149))
        
        radio = QRadioButton("Radio Button")
        textbox = QLineEdit()
        label = QLabel("Label")
        for i in range(len(checkboxList)) :
            Gridlayout.addWidget(checkboxList[i], 1, i)
       
       
        # Gridlayout.setColumnStretch(0, 1)  # คอลัมน์ที่ 0 มีความกว้างเป็นสัดส่วน 1
        # Gridlayout.setColumnStretch(1, 1)  # คอลัมน์ที่ 1 มีความกว้างเป็นสัดส่วน 2     
        Gridlayout.setColumnMinimumWidth(0, 50)  # กำหนดความกว้างขั้นต่ำของคอลัมน์ที่ 0 เป็น 100 พิกเซล
        Gridlayout.setColumnMinimumWidth(1, 50) 
        Gridlayout.setColumnMinimumWidth(2, 50) 
        
        
        # Gridlayout.addWidget(radio, 2, 1)
        # Gridlayout.addWidget(textbox, 2, 0)
        # Gridlayout.addWidget(label, 2, 1)

        frame.setLayout(Gridlayout)
        return frame

    def update_time(self):
        pass

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
