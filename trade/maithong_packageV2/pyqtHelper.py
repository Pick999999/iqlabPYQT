import sys,os 

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, \
QFrame, QLabel, QCheckBox, QPushButton, QLineEdit, QRadioButton,QGridLayout



def createCheckBox(x,y,caption,varname):
    checkbox = QCheckBox(caption)
    checkbox.setObjectName(varname)
    row = x
    col = y
    
    pass

def createTab(tabcaptionArray):
# Tabs
    tabs = QTabWidget()
    for i in range(len(tabcaptionArray)):
        # สร้าง tab 1 อัน
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab_label = QLabel(f"Content of Tab {i}")
        tab_layout.addWidget(tab_label)
        tab.setLayout(tab_layout)
        caption = 'EURUSD' ; varname = 'EURUSD'
        checkbox = QCheckBox(caption)
        checkbox.setObjectName(varname)
        tab_layout.addWidget(checkbox)
        
        # เพิ่มเข้าไปใน tab ใหญ่ 
        tabs.addTab(tab, tabcaptionArray[i])    
    
    return tabs    
    pass

def addCheckBoxToFrame(frame,listOfVar,listOfCaption) : 
    
    # frame.setFrameShape(QFrame.StyledPanel)
    # frame_layout = QGridLayout()
    
    num_checkboxes = len(listOfVar)
    checkboxes_per_row = 5
    # checkbox = QCheckBox("Checkbox")
    # print(listOfVar)
    
    for i in range(num_checkboxes):
        checkbox = QCheckBox(listOfCaption[i])
        checkbox.setObjectName(listOfVar[i])
        row = i // checkboxes_per_row
        col = i % checkboxes_per_row
        frame.addWidget(checkbox, row+2, col)
            
    # for i in range(len(listOfVar)) :
    #     checkbox = QCheckBox(listOfVar[i])
    #     checkbox.setObjectName(listOfCaption[i])
    #     checkbox.setCheckState(True)
    #     # row = i // checkboxes_per_row
    #     row = 1 
    #     col = i
    #     # col = i % checkboxes_per_row
        
    #     frame.addWidget(checkbox, row, col)
        # frame.addWidget(checkbox)
        
    pass

def createFrameWithCheckBox(frameVarName,frameCaption,listOfVar,listOfCaption) :
    # Create a QFrame
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    frame_layout2 = QVBoxLayout()
    
        # Create a caption for the QFrame
    frameCaption = QLabel(frameCaption)
    # frame_layout.addWidget(frameCaption)
    
    caption = QLabel("เลือก สกุลเงิน")
    frame_layout2.addWidget(frameCaption, 5, 5, 11, 5)  # Place the caption at the top-left
    
    num_checkboxes = len(listOfVar)
    checkboxes_per_row = 5
    
    for i in range(num_checkboxes):
        checkbox = QCheckBox(listOfCaption[i])
        checkbox.setObjectName(listOfVar[i])
        row = i // checkboxes_per_row
        col = i % checkboxes_per_row
        frame.addWidget(checkbox, row+2, col)
    
    
    
        
        
        
        
        # Set the layout for the QFrame
    frame.setLayout(frame_layout2)
  

def addChildToFrame(frame,child) :
   
    frame.addWidget(child)
    return 

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("PyQt5 Tabs with Frame Example")
#         self.setGeometry(100, 100, 600, 400)

#         # Create a QTabWidget
#         self.tabs = QTabWidget()
#         self.setCentralWidget(self.tabs)

#         # Create tabs
#         self.tab1 = QWidget()
#         self.tab2 = QWidget()

#         # Add tabs to the QTabWidget
#         self.tabs.addTab(self.tab1, "Tab 1")
#         self.tabs.addTab(self.tab2, "Tab 2")

#         # Create a layout for the first tab
#         self.tab1_layout = QVBoxLayout()

#         # Create a QFrame
#         self.frame = QFrame()
#         self.frame.setFrameShape(QFrame.StyledPanel)
#         self.frame_layout = QVBoxLayout()

#         # Create a caption for the QFrame
#         self.caption = QLabel("Frame Caption")
#         self.frame_layout.addWidget(self.caption)

#         # Create and add widgets to the QFrame
#         self.checkbox = QCheckBox("Checkbox")
#         self.button = QPushButton("Button")
#         self.textbox = QLineEdit("Textbox")
#         self.radio_button = QRadioButton("Radio Button")

#         self.frame_layout.addWidget(self.checkbox)
#         self.frame_layout.addWidget(self.button)
#         self.frame_layout.addWidget(self.textbox)
#         self.frame_layout.addWidget(self.radio_button)

#         # Set the layout for the QFrame
#         self.frame.setLayout(self.frame_layout)

#         # Add the QFrame to the tab layout
#         self.tab1_layout.addWidget(self.frame)

#         # Set the layout for the first tab
#         self.tab1.setLayout(self.tab1_layout)

#         # You can add additional content to the second tab as needed

#         self.show()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = MainWindow()
#     sys.exit(app.exec_())




    

