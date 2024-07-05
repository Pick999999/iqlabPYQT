import sys
import time
from datetime import datetime, timedelta
from PyQt5.QtCore import QTime, QTimer, Qt, QThread, pyqtSignal, QPoint, QDateTime
from PyQt5.QtGui import QPainter, QColor, QPolygon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QLabel

from iqoptionapi.stable_api import IQ_Option

class AnalogClock(QWidget):
    second_changed = pyqtSignal(int)  # Signal to emit current second

    def __init__(self, parent=None):
        super(AnalogClock, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        self.current_time = QTime.currentTime()

    def update_time(self):
        self.current_time = self.current_time.addSecs(1)
        self.second_changed.emit(self.current_time.second())
        self.update()

    def set_time(self, timestamp):
        dt = QDateTime.fromSecsSinceEpoch(timestamp)
        self.current_time = dt.time()
        self.update()

    def paintEvent(self, event):
        side = min(self.width(), self.height())
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
        painter.rotate(30.0 * ((self.current_time.hour() + self.current_time.minute() / 60.0)))
        painter.drawConvexPolygon(hour_hand)
        painter.restore()

        painter.save()
        painter.setBrush(minute_color)
        painter.rotate(6.0 * (self.current_time.minute() + self.current_time.second() / 60.0))
        painter.drawConvexPolygon(minute_hand)
        painter.restore()

        painter.save()
        painter.setBrush(second_color)
        painter.rotate(6.0 * self.current_time.second())
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

class FetchTimeThread(QThread):
    time_fetched = pyqtSignal(int)

    def __init__(self, api, parent=None):
        super(FetchTimeThread, self).__init__(parent)
        self.api = api

    def run(self):
        self.api.connect()
        timestamp = self.api.get_server_timestamp()
        # Convert UTC to ICT (UTC+7)
        ict_time = datetime.utcfromtimestamp(timestamp) + timedelta(hours=7)
        timestamp_ict = int(ict_time.timestamp())
        self.time_fetched.emit(timestamp_ict)

class BuyThread(QThread):
    trade_completed = pyqtSignal(list)  # Signal to emit trade results

    def __init__(self, api, symbols, amounts, directions, durations, parent=None):
        super(BuyThread, self).__init__(parent)
        self.api = api
        self.symbols = symbols
        self.amounts = amounts
        self.directions = directions
        self.durations = durations
        self.main_window = parent  # Store reference to MainWindow

    def run(self):
        # Execute multiple trades
        id_list = self.api.buy_multi(self.amounts, self.symbols, self.directions, self.durations)
        print("Trade IDs:", id_list)
        trade_results = []

        for i, trade_id in enumerate(id_list):
            symbol = self.symbols[i]
            amount = self.amounts[i]
            row_position = self.main_window.table_widget.rowCount()
            self.main_window.table_widget.insertRow(row_position)
            self.main_window.table_widget.setItem(row_position, 0, QTableWidgetItem(str(trade_id)))
            self.main_window.table_widget.setItem(row_position, 1, QTableWidgetItem(symbol))
            self.main_window.table_widget.setItem(row_position, 2, QTableWidgetItem(str(amount)))
            self.main_window.table_widget.setItem(row_position, 3, QTableWidgetItem("Pending"))

        # Sleep for trade duration
        time.sleep(self.durations[0] * 60)  # Assume all trades have the same duration

        for i, trade_id in enumerate(id_list):
            try:
                profit = self.api.check_win_v3(trade_id)
                trade_results.append([trade_id, profit])
            except Exception as e:
                print(f"Error: {e}. Reconnecting...")
                self.api.connect()
                profit = self.api.check_win_v2(trade_id, 2)
                trade_results.append([trade_id, profit])

        self.trade_completed.emit(trade_results)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Threaded Trading Application")
        self.resize(800, 600)
        self.api = IQ_Option("chaikaew902@gmail.com", "Maithong11181")
        self.api.connect()
        self.threads = []
        self.balance = 0
        self.trade_results = []  # To store trade results temporarily
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create frames
        frame1 = QFrame()
        frame2 = QFrame()
        frame3 = QFrame()

        frame1.setFrameShape(QFrame.StyledPanel)
        frame2.setFrameShape(QFrame.StyledPanel)
        frame3.setFrameShape(QFrame.StyledPanel)

        # Layout for frame 1 - Analog Clock
        clock_layout = QVBoxLayout()
        self.clock = AnalogClock()
        self.clock.second_changed.connect(self.handle_second_changed)  # Connect signal to slot
        clock_layout.addWidget(self.clock)
        frame1.setLayout(clock_layout)

        # Layout for frame 2 - Trading buttons
        trade_layout = QVBoxLayout()
        self.trade_button = QPushButton("Trade")
        self.trade_button.clicked.connect(self.start_trading)
        trade_layout.addWidget(self.trade_button)
        
        self.fetch_time_button = QPushButton("Fetch Time")
        self.fetch_time_button.clicked.connect(self.fetch_time)
        trade_layout.addWidget(self.fetch_time_button)
        
        frame2.setLayout(trade_layout)

        # Layout for frame 3 - Trade results and balance
        result_layout = QVBoxLayout()
        self.balance_label = QLabel("Balance: $0")
        result_layout.addWidget(self.balance_label)
        self.table_widget = QTableWidget(0, 4)
        self.table_widget.setHorizontalHeaderLabels(["Trade ID", "Currency", "Amount", "Profit"])
        result_layout.addWidget(self.table_widget)
        frame3.setLayout(result_layout)

        # Add frames to main layout
        layout.addWidget(frame1)
        layout.addWidget(frame2)
        layout.addWidget(frame3)

        self.setLayout(layout)

    def fetch_time(self):
        fetch_thread = FetchTimeThread(self.api)
        fetch_thread.time_fetched.connect(self.update_clock_time)
        fetch_thread.start()
        self.threads.append(fetch_thread)

    def update_clock_time(self, timestamp):
        self.clock.set_time(timestamp)

    def handle_second_changed(self, second):
        # print(f"Second changed: {second}")  # Debug message
        if second == 10:
            print("Fetching data from API...")
            # Add code to fetch data from API
        elif second == 20:
            print("Starting auto trade...")
            self.start_trading()
        elif second == 0:
            print("Updating profit...")
            self.update_trade_profits()

    def start_trading(self):
        symbols = ["EURUSD-OTC", "EURGBP-OTC"]
        amounts = [1, 1]
        directions = ["call", "call"]
        durations = [1, 1]

        trade_thread = BuyThread(self.api, symbols, amounts, directions, durations, self)
        trade_thread.trade_completed.connect(self.store_trade_results)
        trade_thread.start()
        self.threads.append(trade_thread)

    def store_trade_results(self, trade_results):
        print(f"Trade results: {trade_results}")  # Debug message
        self.trade_results = trade_results

    def update_trade_profits(self):
        
        print(f"Updating profits for trades: {self.trade_results}")  # Debug message
        for trade_id, profit in self.trade_results:
            rows = self.table_widget.rowCount()
            for row in range(rows):
                item = self.table_widget.item(row, 0)
                if item and int(item.text()) == trade_id:
                    self.table_widget.setItem(row, 3, QTableWidgetItem(f"{profit:.2f}"))
                    self.update_balance(profit)
                    break

    def update_balance(self, profit):
        self.balance += profit
        self.balance_label.setText(f"Balance: ${self.balance:.2f}")

    def closeEvent(self, event):
        for thread in self.threads:
            thread.quit()
            thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
