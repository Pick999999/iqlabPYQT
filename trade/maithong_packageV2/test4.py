import sys
import threading
import time
import random  # แทนที่ด้วยการดึงข้อมูลจริงจาก IQOption
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 300)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.start_button = QtWidgets.QPushButton("Start", self.centralwidget)
        self.start_button.setObjectName("start_button")
        self.verticalLayout.addWidget(self.start_button)
        
        self.data_label = QtWidgets.QLabel(self.centralwidget)
        self.data_label.setAlignment(QtCore.Qt.AlignCenter)
        self.data_label.setObjectName("data_label")
        self.verticalLayout.addWidget(self.data_label)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.data = []
        self.sma_value = 0
        
        self.start_button.clicked.connect(self.start_threads)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.data_label.setText(_translate("MainWindow", "Data will be shown here"))

    def start_threads(self):
        self.data_thread = threading.Thread(target=self.fetch_data)
        self.data_thread.daemon = True
        self.data_thread.start()

        self.sma_thread = threading.Thread(target=self.calculate_sma)
        self.sma_thread.daemon = True
        self.sma_thread.start()

    def fetch_data(self):
        while True:
            time.sleep(1)
            new_data = random.randint(1, 100)  # แทนที่ด้วยการดึงข้อมูลจริงจาก IQOption
            self.data.append(new_data)
            QtCore.QMetaObject.invokeMethod(self.data_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, f"New Data: {new_data}"))

    def calculate_sma(self):
        while True:
            time.sleep(30)
            if len(self.data) >= 5:  # สมมติว่าคำนวณ SMA จากข้อมูล 5 ค่า
                self.sma_value = sum(self.data[-5:]) / 5
                print(f"SMA: {self.sma_value}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
