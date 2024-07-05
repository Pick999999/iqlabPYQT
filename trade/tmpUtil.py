
from iqoptionapi.stable_api import IQ_Option

from iqoptionapi.stable_api import IQ_Option
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtGui import QPainter, QPolygon, QColor, QFont,QBrush
import math,os
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPolygon, QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QWidget, QPushButton, QButtonGroup, QHBoxLayout, QMenuBar, QListWidget,  \
    QTabWidget, QMenu, QLabel,QFrame,QCheckBox,QLineEdit,QRadioButton,QGridLayout, QMessageBox
from PyQt5.QtCore import QTime, QDateTime    
import sys



 



def toTrade(I_want_money,curpair,action) :
    
    Money=  1     
    expirations_mode=1

    check,id=I_want_money.buy(Money,curpair,action,expirations_mode)
    if check:
      print("!buy!")
    else:
      print("buy fail")


def buyMulti(I_want_money) :

    Money=[] ; curpairTrade=[] ; ACTION=[] ;expirations_mode=[]

    Money.append(1)
    curpairTrade.append("EURUSD")
    ACTION.append("call")#put
    expirations_mode.append(1)

    Money.append(1)
    curpairTrade.append("EURAUD")
    ACTION.append("call")#put
    expirations_mode.append(1)

    print("buy multi")
    id_list=I_want_money.buy_multi(Money,curpairTrade,ACTION,expirations_mode)
        
    print("check win only one id (id_list[0])")
    print(I_want_money.check_win_v2(id_list[0],2))
    
def show_message_box(message):
        
      msg_box = QMessageBox()
      msg_box.setWindowTitle("Message Box")
      msg_box.setText(message)
      msg_box.exec()    
      

def createFrame2(self) :
    # หลักการสร้าง frame
    # 1. สร้าง Layout --> layout = QVBoxLayout()
    # 2. สร้าง รายการ Element
    # 3. เพิ่ม รายการ Element เข้าไปยัง layout ด้วย layout.addWidget(self.trade_button)
    # 4. สร้่าง frame -->frame = QFrame()
    # 5. เพิ่ม layout เข้าไปที่ frame ด้วย frame.setLayout(layout) 
    frame2 = QFrame()
    frame2.setFrameShape(QFrame.StyledPanel)
    trade_layout = QVBoxLayout()
    self.trade_button = QPushButton("Trade")
    self.trade_button.clicked.connect(self.start_trading)
    
    
    trade_layout.addWidget(self.trade_button)
     
    self.labeltimeserver = QLabel() 
    self.labeltimeserver.setText("-9999")    
    
    self.fetch_time_button = QPushButton("Fetch Time")
    self.fetch_time_button.clicked.connect(self.fetch_time)
    trade_layout.addWidget(self.fetch_time_button)        
    trade_layout.addWidget(self.labeltimeserver)        
    frame2.setLayout(trade_layout)
    
    return frame2
    
def createFrame3(self) :
    
    frame3 = QFrame()
    frame3.setFrameShape(QFrame.StyledPanel)
    
    # Layout for frame 3 - Trade results and balance
    result_layout = QVBoxLayout()
    self.balance_label = QLabel("Balance: $0")
    result_layout.addWidget(self.balance_label)
    self.table_widget = QTableWidget(0, 5)
    self.table_widget.setHorizontalHeaderLabels(["Trade ID", "Currency","Action", "Amount", "Profit"])
    result_layout.addWidget(self.table_widget)
    frame3.setLayout(result_layout)
    
    return frame3