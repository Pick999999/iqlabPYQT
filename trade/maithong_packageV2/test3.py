import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt

class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        grid = QGridLayout()

        # Custom function to add widgets with default alignment
        def add_widget_with_default_alignment(widget, row, col):
            grid.addWidget(widget, row, col, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Create buttons
        btn1 = QPushButton("Button 1")
        btn2 = QPushButton("Button 2")
        btn3 = QPushButton("Button 3")
        btn4 = QPushButton("Button 4")

        # Add buttons to grid layout using custom function
        add_widget_with_default_alignment(btn1, 0, 0)
        add_widget_with_default_alignment(btn2, 0, 1)
        add_widget_with_default_alignment(btn3, 1, 0)
        add_widget_with_default_alignment(btn4, 1, 1)

        # Set column width and row height
        grid.setColumnMinimumWidth(0, 100)
        grid.setColumnMinimumWidth(1, 100)
        grid.setRowMinimumHeight(0, 50)
        grid.setRowMinimumHeight(1, 50)

        # Set column and row stretch
        grid.setColumnStretch(0, 1) ; grid.setRowStretch(0, 1)
        grid.setColumnStretch(1, 1) ; grid.setRowStretch(1, 1)
        
        

        self.setLayout(grid)

        self.setWindowTitle('QGridLayout with Default Alignment Example')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
