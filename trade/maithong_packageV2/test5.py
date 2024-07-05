from PyQt5 import QtWidgets, QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(50, 50, 700, 400))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(6)
        
        currencies = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF", "NZD/USD"]
        button_texts = ["Idle", "Put", "Call", "Signal"]

        for row in range(6):
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(currencies[row]))
            self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem("Balance"))
            for col in range(1, 5):
                button = QtWidgets.QPushButton(button_texts[col-1])
                button.setCheckable(True)
                button.clicked.connect(self.create_button_callback(row, currencies[row], button_texts[col-1], button))
                self.tableWidget.setCellWidget(row, col, button)
        
        MainWindow.setCentralWidget(self.centralwidget)

    def create_button_callback(self, row, currency, action, button):
        def on_button_clicked():
            self.buttonClicked(row, currency, action, button)
        return on_button_clicked

    def buttonClicked(self, rowno, currency, action, button):
        print(f"Button clicked in row {rowno}: {currency} - {action}")
        button.setStyleSheet("background-color: yellow")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
