import sys,os
import sys,os,time

# from maithong_packageV2 import pdatetime,mylib,clsCandleArray
# sys.path.append(os.path.join(os.path.dirname(__file__), '\maithong_packageV2'))



import math
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPolygon, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QButtonGroup, QHBoxLayout, QMenuBar, QListWidget, QTabWidget, QMenu, QLabel, QMessageBox

class AnalogClock(QWidget):
    def __init__(self, parent=None):
        
         
        super(AnalogClock, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.setWindowTitle('Analog Clock')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # Update every second



    def paintEvent(self, event):
        side = min(self.width(), self.height())
        time = QTime.currentTime()

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
        painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        painter.drawConvexPolygon(hour_hand)
        painter.restore()

        painter.save()
        painter.setBrush(minute_color)
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(minute_hand)
        painter.restore()

        painter.save()
        painter.setBrush(second_color)
        painter.rotate(6.0 * time.second())
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Currency Pairs Table')
        self.setGeometry(100, 100, 800, 600)

        # Create a menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        view_menu = menubar.addMenu('View')

        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create a horizontal layout for the clock and counter
        clock_layout = QHBoxLayout()

        # Add the analog clock to the main layout
        self.analog_clock = AnalogClock(self)
        clock_layout.addWidget(self.analog_clock)

        # Add the label and counter
        self.label = QLabel("กำลังรอผล...", self)
        self.counter_label = QLabel("", self)
        clock_layout.addWidget(self.label)
        clock_layout.addWidget(self.counter_label)

        layout.addLayout(clock_layout)

        # Timer to update the counter
        self.counter_timer = QTimer(self)
        self.counter_timer.timeout.connect(self.update_counter)
        self.counter_timer.start(1000)  # Update every second

        # Create a tab widget
        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        # Create the first tab
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)

        # Create a table for the first tab
        self.table1 = QTableWidget(self)
        self.table1.setRowCount(5)  # Adjust the row count as needed
        self.table1.setColumnCount(3)
        self.table1.setHorizontalHeaderLabels(['Currency Pair', 'Toggle Buttons', 'Balance'])

        # Set the column widths
        self.table1.setColumnWidth(0, 200)  # Set the width of the first column
        self.table1.setColumnWidth(1, 300)  # Set the width of the second column
        self.table1.setColumnWidth(2, 100)  # Set the width of the third column

        # Populate the table
        currency_pairs = ['EUR/USD', 'EUR/GBP', 'EUR/JPY', 'EUR/AUD', 'EUR/CAD']
        for i, pair in enumerate(currency_pairs):
            self.table1.setItem(i, 0, QTableWidgetItem(pair))

            # Create a widget to hold the toggle buttons
            toggle_widget = QWidget(self)
            toggle_layout = QHBoxLayout(toggle_widget)
            toggle_layout.setContentsMargins(0, 0, 0, 0)
            button_group = QButtonGroup(self)

            buttonLabel = ['IDLE','CALL','PUT','By Signal']
            for j in range(4):
                # button = QPushButton(f'Button {j + 1}', self)
                self.button = QPushButton(buttonLabel[j], self)
                self.button.setCheckable(True)
                button_group.addButton(self.button)
                toggle_layout.addWidget(self.button)
                self.button.clicked.connect(self.showMessageBox)
                

            # Check the first button by default
            button_group.buttons()[0].setChecked(True)
            
            self.table1.setCellWidget(i, 1, toggle_widget)
            self.table1.setItem(i, 2, QTableWidgetItem('1000'))  # Example balance value

        # Create a list widget for the first tab
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(['EUR/USD', 'EUR/GBP', 'EUR/JPY', 'EUR/AUD', 'EUR/CAD'])

        # Add the table and list widget to the first tab layout
        tab1_layout.addWidget(self.table1)
        tab1_layout.addWidget(self.list_widget)

        self.tab_widget.addTab(tab1, "Tab 1")

        # Create the second tab
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)

        # Create a table for the second tab
        self.table2 = QTableWidget(self)
        self.table2.setRowCount(5)  # Adjust the row count as needed
        self.table2.setColumnCount(3)
        self.table2.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])

        # Set the column widths for the second table
        self.table2.setColumnWidth(0, 150)
        self.table2.setColumnWidth(1, 150)
        self.table2.setColumnWidth(2, 150)

        # Populate the table for the second tab
        for i in range(5):
            self.table2.setItem(i, 0, QTableWidgetItem(f'Item {i + 1}'))
            self.table2.setItem(i, 1, QTableWidgetItem(f'Data {i + 1}'))
            self.table2.setItem(i, 2, QTableWidgetItem(f'Value {i + 1}'))

        tab2_layout.addWidget(self.table2)

        self.tab_widget.addTab(tab2, "Tab 2")
        
    def showMessageBox(self):
        # สร้าง Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("Additional information can go here.")
        msg.setWindowTitle("Message Box Title")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        # แสดง Message Box
        retval = msg.exec_()
        print("Dialog return value:", retval)    

    def update_counter(self):
        current_time = QTime.currentTime()
        second = current_time.second()

        if 0 <= second <= 30:
            countdown = 30 - second
            self.label.setText("กำลังนับถอยหลัง...")
            label_font = QFont()
            label_font.setPointSize(16)  # Set font size for QLabel
            self.label.setFont(label_font)
            # self.label.setFontSize(16)  # Set font size for QLabel
        else:
            countdown = 60 - second
            self.label.setText("รอผล")

        self.counter_label.setText(str(countdown))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())

'''
1.เพิ่ม option ว่าจะให้ trade แบบ
   1.1 ชนะครั้งเดียวแล้ว  Idle 
   1.2 วนลูปตาม  ema3 slope จนได้ ema3 กลับตัว
   1.3 วนลูปตาม  Button->call,put
   1.4 วนลูปตาม  ได้ Balance
2.เพิ่มการตั้งค่า get action
  2.1  ema3 slope
  2.2  macd 
  2.3  adx checkbox +  textbox 3 อัน
  2.4  rsi
  2.5  stochastics 
3.เพิ่มเงือนไขการเดินเงิน
  3.1 เท่ากันทุกตา
  3.2 Martingale แบบ Balance*2
  3.3 Martingale แบบ กำหนดเอง
  3.4 Martingale แบบ ดึงยอดกำไรมาทบ
  
  
  
'''