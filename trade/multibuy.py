import sys
import time
from datetime import datetime, timedelta
from PyQt5.QtCore import QTime, QTimer, Qt, QThread, pyqtSignal, QPoint, QDateTime
from PyQt5.QtGui import QPainter, QColor, QPolygon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QLabel

from iqoptionapi.stable_api import IQ_Option
import tmpUtil,mylib
from clsCandleArray import CandleArray

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

    def __init__(self, api, symbols, amounts, directions, durations,ObjList, parent=None):
        
        super(BuyThread, self).__init__(parent)
        self.api = api
        self.symbols2 = []
        self.amounts2 = []
        for i  in range(len(ObjList)) :
            
            if ObjList[i]['WinCon'] == 0 :
                
               self.symbols2.append(symbols[i])            
               self.amounts2.append(ObjList[i]['MoneyTrade'])
               self.directions = directions
               self.durations = durations
               
        self.main_window = parent  # Store reference to MainWindow
        self._is_running = True

    def run(self):
        
        # Execute multiple trades
        # id_list = self.api.buy_multi(self.amounts, self.symbols, self.directions, self.durations)
        print("จำนวน Currency = " , len(self.symbols2))
        print("Amount  = " , self.amounts2 , ' Type =',type(self.amounts2))
        
        if len(self.symbols2) == 0 :
           message = 'ชนะ ครบทุกสกุลเงิน '  
           print(message)        
           sys.exit(0)
           
        if len(self.symbols2) == 1 :           
            expirations_mode = 1
            trade_results = []
            self.directions = 'call' ; self.durations  = expirations_mode            
            print('เทรด  = ', self.symbols2[0] ,' = ',self.amounts2)            
            check ,id = self.api.buy(self.amounts2[0], self.symbols2[0], self.directions, self.durations)  
            if check:
               print("!buy ! ", self.symbols2[0] ,' = ' , self.amounts2[0])
            trade_id = id
            symbol = self.symbols2[0]
            
            row_position = self.main_window.table_widget.rowCount()
            self.main_window.table_widget.insertRow(row_position)
            self.main_window.table_widget.setItem(row_position, 0, QTableWidgetItem(str(trade_id)))
            self.main_window.table_widget.setItem(row_position, 1, QTableWidgetItem(symbol))
            self.main_window.table_widget.setItem(row_position, 2, QTableWidgetItem(self.directions))
            self.main_window.table_widget.setItem(row_position, 3, QTableWidgetItem(str(self.amounts2[0])))
            self.main_window.table_widget.setItem(row_position, 4, QTableWidgetItem("Pending"))
            
            profit = self.api.check_win_v3(id)
            print(id,'=',profit)
            trade_results.append([trade_id, profit])
            self.trade_completed.emit(trade_results)
            return 
                    
        else :
            id_list = self.api.buy_multi(self.amounts2, self.symbols2, self.directions, self.durations)           
            print("Trade IDs:", id_list)
            trade_results = []
            numBuySuccess = 0  ; numBuyFail = 0 
            for i, trade_id in enumerate(id_list):
                if trade_id == None or str(trade_id) == 'None':
                   numBuyFail = numBuyFail + 1                     
                else :
                   numBuySuccess =  numBuySuccess +1 
                    
            print('Num Buy Success=',numBuySuccess) 

            for i, trade_id in enumerate(id_list):
                symbol = self.symbols2[i]
                amount = self.amounts2[i]
                row_position = self.main_window.table_widget.rowCount()
                self.main_window.table_widget.insertRow(row_position)
                self.main_window.table_widget.setItem(row_position, 0, QTableWidgetItem(str(trade_id)))
                self.main_window.table_widget.setItem(row_position, 1, QTableWidgetItem(symbol))
                self.main_window.table_widget.setItem(row_position, 2, QTableWidgetItem(self.directions[i]))
                self.main_window.table_widget.setItem(row_position, 3, QTableWidgetItem(str(amount)))
                self.main_window.table_widget.setItem(row_position, 4, QTableWidgetItem("Pending"))
                

            # Sleep for trade duration
            # time.sleep(self.durations[0] * 60)  # Assume all trades have the same duration
            profit = self.api.check_win_v3(trade_id)
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
        self.initUI()
        self.InitVar()
        
        
    def InitVar(self) :
        data = []
        self.tradeno = 0
        
        self.symbols = ["EURUSD-OTC", "USDJPY-OTC"]
        if self.tradeno == 0 :
           self.ObjList = self.InitSymBols(self.symbols)
        
        
        self.directions = []
        self.thistimestamp = time.time()
        
        
        self.curpair = self.symbols[0]
        Candle1 = CandleArray(self.curpair,self) 
        lastIndex = 15
        print('Color =',Candle1.AnalyData[lastIndex]['bodyData']['Color'])
        # print('EMA3 In Main =',Candle1.AnalyData[lastIndex]['macd']['ema3'])
        print('Slope In Main =',Candle1.AnalyData[lastIndex]['macd']['analysis']['slope3Value'],Candle1.AnalyData[lastIndex]['macd']['analysis']['slopeDirection3'] )   
        
        if Candle1.AnalyData[lastIndex]['macd']['analysis']['slopeDirection3'] == 'UP' :
           self.directions.append('call')
        else :
           self.directions.append('put') 
           
           
        self.curpair = self.symbols[1]
        Candle2 = CandleArray(self.curpair,self)
        print('Color =',Candle2.AnalyData[lastIndex]['bodyData']['Color'])
        # print('EMA3 In Main =',Candle2.AnalyData[lastIndex]['macd']['ema3'])
        print('Slope In Main2 =',Candle2.AnalyData[lastIndex]['macd']['analysis']['slope3Value'],Candle1.AnalyData[lastIndex]['macd']['analysis']['slopeDirection3'] )   
        if Candle2.AnalyData[lastIndex]['macd']['analysis']['slopeDirection3'] == 'UP' :
           self.directions.append('call')
        else :
           self.directions.append('put') 
        
        
        # data.append(CandleArray('EURGBP-OTC'))

    def initUI(self):
        
        mainlayout = QVBoxLayout()

        # Create frames
        frame1 = QFrame()
        # frame2 = QFrame()
        frame3 = QFrame()

        frame1.setFrameShape(QFrame.StyledPanel)
        # frame2.setFrameShape(QFrame.StyledPanel)
        frame3.setFrameShape(QFrame.StyledPanel)
        
        # Layout for frame 1 - Analog Clock
        clock_layout = QVBoxLayout()
        self.clock = AnalogClock()
        self.clock.second_changed.connect(self.handle_second_changed)  # Connect signal to slot
        clock_layout.addWidget(self.clock)
        frame1.setLayout(clock_layout)

        
        frame2  =tmpUtil.createFrame2(self)
        frame3  =tmpUtil.createFrame3(self)

        # Add frames to main layout
        mainlayout.addWidget(frame1)
        mainlayout.addWidget(frame2)
        mainlayout.addWidget(frame3)

        self.setLayout(mainlayout)

    def fetch_time(self):
        
        fetch_thread = FetchTimeThread(self.api)
        fetch_thread.time_fetched.connect(self.update_clock_time)
        fetch_thread.start()
        self.threads.append(fetch_thread)

    def update_clock_time(self, timestamp):
        
        self.thistimestamp = timestamp
        self.clock.set_time(timestamp)
        self.labeltimeserver.setText(str(timestamp))

    def handle_second_changed(self, second):
        
        self.thistimestamp = self.thistimestamp+1
        self.labeltimeserver.setText(str(self.thistimestamp))
        if second == 10:
            print("Fetching data from API...")
            # Add code to fetch data from API
        elif second == 20 :
            print("Starting auto trade...")
            self.start_trading()
            
    def InitSymBols(self,curpairList):
        
        ObjList= []
        no = 0
        for i in range(len(curpairList)) :
           Obj = {
              "curpair" : curpairList[no],
              "sugguestaction" :"",
              "action" :"",
              "MoneyTrade" : 2,
              "LastWin" : "",              
              "WinCon" : 0 ,
              "profit" : 0,
              "balance": 0
           }
           no = no +1
           ObjList.append(Obj)
           
        return ObjList

    def start_trading(self):
        
        
        symbols = self.symbols
        # if self.tradeno == 0 :
        #    self.ObjList = self.InitSymBols(symbols)
        
        # amounts = [1, 1]
        
        directions = self.directions
        amounts = []
        directions = []
        directions = ["call", "call"]
        durations = []
        directions = self.directions
        for i in range(len(self.ObjList)) :       
            if self.ObjList[i]['WinCon'] == 0 :
               symbols.append(self.ObjList[i]['curpair']) 
               amounts.append(self.ObjList[i]['MoneyTrade'])
               durations.append(1)
               
        print(self.ObjList)       
        self.tradeno = self.tradeno + 1
        
        
        # durations = [1, 1]

        trade_thread = BuyThread(self.api, symbols, amounts, directions, durations,self.ObjList, parent=self)
        trade_thread.trade_completed.connect(self.trade_callback)
        trade_thread.finished.connect(lambda t=trade_thread: self.cleanup_thread(t))
        self.threads.append(trade_thread)
        trade_thread.start()

    def cleanup_thread(self, trade_thread):
        def wrapped():
            if trade_thread in self.threads:
                self.threads.remove(trade_thread)
        return wrapped

    def trade_callback(self, trade_results):
        #  Update Profit
        for trade_id, profit in trade_results:
            rows = self.table_widget.rowCount()
            for row in range(rows):
                item = self.table_widget.item(row, 0)
                curpair = self.table_widget.item(row, 1)
                print('curpair =',curpair.text(), ' Profit=',profit)
                if item and int(item.text()) == trade_id:
                    self.table_widget.setItem(row, 4, QTableWidgetItem(f"{profit:.2f}"))
                    self.update_balance(profit,curpair.text())
                    break

    def update_balance(self, profit,curpair):
        self.balance += profit 
        balanceThai = self.balance *35 
        self.balance_label.setText(f"Balance: ${self.balance:.2f} Balance: บาท{balanceThai:.2f}")
        # self.labeltimeserver.setText(str(self.balance*35))
        for i in range(len(self.ObjList)) :
            if curpair == self.ObjList[i]['curpair'] :
               if profit > 0 :
                self.ObjList[i]['LastWin'] = "Win"  
                self.ObjList[i]['WinCon'] = self.ObjList[i]['WinCon']  +1
               else :
                 self.ObjList[i]['LastWin'] = "Loss" 
               
               self.ObjList[i]['balance'] = self.ObjList[i]['balance'] + profit
               print('Balance = ',self.ObjList[i]['curpair'],'=',self.ObjList[i]['balance'])
               if self.ObjList[i]['balance'] < 0 :
                  self.ObjList[i]['MoneyTrade'] = int(abs(self.ObjList[i]['balance'])*2)
                  print ('Next Money = ',self.ObjList[i]['curpair'],'=',self.ObjList[i]['MoneyTrade'] )
       
        numCurPairToTrade = 0  
        for i in range(len(self.ObjList)) :
            if self.ObjList[i]['WinCon'] == 0 :
               numCurPairToTrade = numCurPairToTrade +1 
        if numCurPairToTrade == 0 :
           totalBalance = 0 
           for i in range(len(self.ObjList)) :
               totalBalance =  totalBalance + self.ObjList[i]['balance']
               
           tmpUtil.show_message_box("Finshed Job") 
           msg = "Finished Job"
           message = "Trade Results:\n"
           message += "{:<10} {:<10} {:<10}\n".format("Currency", "MoneyTrade", "Balane")
           message += "-"*30 + "\n"
           for item in self.ObjList:
                message += "{:<10} {:<10} {:<10.2f}\n".format(item["curpair"], str(item["MoneyTrade"]), item["balance"])

           message += '\n****************************\n'
           totalBalance = round(totalBalance,2)
           totalBath =  totalBalance*35 
           message += ' Balance = $' + str(totalBalance) + '\n'
           message += ' Balance บาท = ฿' + str(totalBath) + '\n'
           
           
           mylib.lineNotify(message)
           sys.exit(0)
                

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


 