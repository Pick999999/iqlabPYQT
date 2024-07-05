import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QFrame, QGridLayout, QCheckBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Checkbox Grid Example")
        self.setGeometry(100, 100, 600, 400)

        # Create a QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create a tab
        self.tab = QWidget()
        self.tabs.addTab(self.tab, "Tab 1")

        # Create a layout for the tab
        self.tab_layout = QVBoxLayout()

        # Create a QFrame
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame_layout = QGridLayout()

        # Create and add QCheckBox widgets to the QGridLayout
        num_checkboxes = 10
        checkboxes_per_row = 5
        for i in range(num_checkboxes):
            checkbox = QCheckBox(f"Checkbox {i + 1}")
            row = i // checkboxes_per_row
            col = i % checkboxes_per_row
            self.frame_layout.addWidget(checkbox, row, col)

        # Set the layout for the QFrame
        self.frame.setLayout(self.frame_layout)

        # Add the QFrame to the tab layout
        self.tab_layout.addWidget(self.frame)

        # Set the layout for the tab
        self.tab.setLayout(self.tab_layout)

        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
