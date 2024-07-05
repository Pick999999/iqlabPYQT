import json ,time
import pdatetime
import talib
import requests
import numpy as np
import pandas as pd
import math
# from clsCandle import Candle,json_data
import indicatorTALIB as indicatorTALIB
import candleType 
import mylib

class CandleArray:
    
    def __init__(self,curpair,parent=None):
        
        # rawCandle = ตัวแปร array ของข้อมูลดิบทั้งหมด 30 รายการ
        # rawCandleTmp = ตัวแปร ของข้อมูลดิบ 1 รายการ
        # Information = ตัวแปร array ของข้อมูลที่ทำการสร้าง Indy จาก rawCandle แล้ว ทั้งหมด 30 รายการ
        # Step1  ให้ทำการ ดึงข้อมูล 30 รายการจาก iqoption มาใส่ใน rawCandle
        # Step2  นำข้อมูล rawCandle ไปสร้าง indy แล้วเก็บไว้ใน Information ซึ่งจะมีทั้งหมด 30 รายการ
        # Step3  นำข้อมูล Information มาหา action แล้วส่งไป Buy
        # Step4   เข้่ารอบ เทรดที่ 2,3... 
        # Step4.1 ดึงข้อมูลจาก iq มา 1 รายการ ใส่ใน tmp 
        # Step4.2 นำ tmp  ไป append->rawCandle
        # Step4.3 วนไปที่ Step3
        
        # super(CandleArray, self).__init__(parent)
        self.curpair = curpair
        self.parent = parent  # Save parent
        numcandleFirst = 30 ; numcandleNext = 1
        
        self.timeinterval = 60 
        # self.getRawCandleFirst(curpair, timeinterval, numcandleFirst, parent.thistimestamp)
        # candle = mylib.getCandle(I_want_money, curpair, numcandle,timeserver)
        # self.printCurPair()
    
    
    def giverawCandle(self):
        
        self.parent.thistimestamp
        if self.parent.tradeno == 0 :
           numcandle = 30
           self.tmpData = self.parent.api.get_candles(self.curpair, self.timeinterval, numcandle,self.parent.thistimestamp)
        else :
           numcandle = 1
           self.tmpData = self.parent.api.get_candles(self.curpair, self.timeinterval, numcandle,self.parent.thistimestamp)
                        
        
        
        
        
    def getRawCandleFirst(self,curpair, timeinterval, numcandle, LastCandleTimestamp) :
        
        self.rawcandleList = self.parent.api.get_candles(curpair, timeinterval, numcandle, LastCandleTimestamp)
        self.AnalyData = []
        for i in range(len(self.rawcandleList)) :
            jsonData = self.createAnalyData_Step1(curpair,self.rawcandleList[i])  
            self.AnalyData.append(jsonData)
            
        
        # Step นี้ สร้างเฉพาะ หมวด macd
        self.createMACD()
        lastIndex = len(self.AnalyData)-1
        # print('Last Slope =',self.AnalyData[lastIndex]['macd']['analysis']['slopeDirection3'] )
        
    def getNextCandle(self,curpair, timeinterval, numcandle, LastCandleTimestamp) :
        numcandle = 1 
        self.rawcandleTmp = self.parent.api.get_candles(curpair, timeinterval, numcandle, LastCandleTimestamp)
        self.AnalyData = []
        for i in range(len(self.rawcandleList)) :
            jsonData = self.createAnalyData_Step1(curpair,self.rawcandleList[i])  
            self.AnalyData.append(jsonData)
            
        
        # Step นี้ สร้างเฉพาะ หมวด macd
        self.createMACD()
    
    
    def createIndy(self) :
        pass
        
    def createMACD(self) :
        fastperiod = 3 ; slowperiod = 5 ; signalperiod = 4
        high_prices = self.getPricesNumpy(self.AnalyData,'max')
        low_prices = self.getPricesNumpy(self.AnalyData,'min')
        close_prices = self.getPricesNumpy(self.AnalyData,'close')   
        open_prices = self.getPricesNumpy(self.AnalyData,'open')                
        
        macd, macdsignal, macdhist = talib.MACD(close_prices, fastperiod, slowperiod, signalperiod)     
        # คำนวณค่า EMA
        ema3 = talib.EMA(close_prices, timeperiod=3)
        ema5 = talib.EMA(close_prices, timeperiod=5)
        ema9 = talib.EMA(close_prices, timeperiod=6)
        ema3 = np.nan_to_num(ema3, nan=0.0)
        ema5 = np.nan_to_num(ema5, nan=0.0)
        ema9 = np.nan_to_num(ema9, nan=0.0)
        
        macd = np.nan_to_num(macd, nan=0.0)
        macdhist = np.nan_to_num(macdhist, nan=0.0)
        macdsignal = np.nan_to_num(macdsignal, nan=0.0)
        loopno = 0
        for i in range(len(self.AnalyData)):            
            
            self.AnalyData[i]['macd']['ema3'] = ema3[i]
            self.AnalyData[i]['macd']['ema5'] = ema5[i]
            self.AnalyData[i]['macd']['ema9'] = ema9[i]
            self.AnalyData[i]['macd']['macd'] = macd[i]
            self.AnalyData[i]['macd']['signalLine'] = macdsignal[i]
            self.AnalyData[i]['macd']['histogram'] = macdhist[i]
            
            emaAbove = ''                         
            if self.AnalyData[i]['macd']['ema3']  > self.AnalyData[i]['macd']['ema5'] : emaAbove = '3Above5'
            if self.AnalyData[i]['macd']['ema3']  < self.AnalyData[i]['macd']['ema5'] : emaAbove = '5Above3'                
            self.AnalyData[i]['macd']['analysis']['emaAbove']  = emaAbove
            if loopno > 0 :
               slope3Diff = self.AnalyData[i]['macd']['ema3'] - self.AnalyData[i-1]['macd']['ema3'] *1000
               self.AnalyData[i]['macd']['analysis']['slope3Value'] = slope3Diff
               if (slope3Diff) > 0 :
                  if slope3Diff <= 10 :                   
                     self.AnalyData[i]['macd']['analysis']['slopeDirection3'] = 'Paralell'
                     self.AnalyData[i]['macd']['analysis']['slopeDirection3'] = 'UP'    
                  else :
                     self.AnalyData[i]['macd']['analysis']['slopeDirection3'] = 'UP'    
               else:    
                 self.AnalyData[i]['macd']['analysis']['slopeDirection3'] = 'DOWN' 
            loopno = loopno +1      
                
        
    def getNextRawCandle(self,curpair, timeinterval, numcandle, LastCandleTimestamp) :
        
        numcandle = 1
        self.tmpCandle = self.parent.api.get_candles(curpair, timeinterval, numcandle, LastCandleTimestamp)
        
    def printCurPair(self):    
        print(self.parent.curpair)
        
    def createAnalyData_Step1(self,curpair,rawData)    :
        
        
        json_data =  {
            "curpair": curpair,  
            "dataMultiply" : 1000000,
            "candleCode": "",
            "minuteno":  pdatetime.B22_cvTimestamp2TimeStr_NoSecond(rawData['from']),
            "RawData": {
                "id": 0,      
                "minuteno":  pdatetime.B22_cvTimestamp2TimeStr_NoSecond(rawData['from']),  
                "from": rawData['from'],
                "at": rawData['at'],
                "to": rawData['to'],
                "open": rawData['open'],
                "close": rawData['close'],
                "min": rawData['min'],
                "max": rawData['max'],
                "volume": rawData['volume']
            },
            "bodyData": {
                "Color": "",
                "CandleHeight": 0.0,
                "BodyHeight": 0.0,
                "UHeight": 0.0,
                "LHeight": 0.0,
                "BodyHeightPercent": 0.0,
                "UHeightPercent": 0.0,
                "LHeightPercent": 0.0,
                "CandleType": ""
            },
            "macd": {
                "ema3": 0.0,
                "ema5": 0.0,
                "ema9": 0.0,
                "macd": 0.0,
                "signalLine": 0.0,
                "analysis": {
                    "slope3Value": "",
                    "slopeDirection3": "",
                    "slopeDirection5": "",
                    "slopeDirection9": "",
                    "emaAbove": "3",
                    "emaConflict" : "",
                    "ConvergenceType": 0.0,
                    "ConvergenceType": "",
                    "TurnPointType": "",
                    "IdOfLastTurnPoint": "",
                    "TurnPointNo": 0,
                    "CutPointType": ""
                }
            },
            "Bollinger": {
                "U": 1
            },
            "RSI": {
                "U": 1
            },
            "atr": {
                "U": 1
            },
            "trade": {
                "tradeno": 1,
                "action": "",
                "MoneyTrade": 0,
                "profit": 0.0,
                "balance": 0.0
            }
        }
        
        bodyData = self.AnalyzeBody(json_data)
        json_data['bodyData']['Color'] =  bodyData['Color']
        
        return json_data

    
    def checkCutPointof2Array(arrayFast,arraySlow) :
        # รับ Input เป็น array
        crosses = []
        for i in range(1, len(arrayFast)):
            if (arrayFast[i-1] < arraySlow[i-1] and arrayFast[i] > arraySlow[i]) or \
            (arrayFast[i-1] > arraySlow[i-1] and arrayFast[i] < arraySlow[i]):
               crosses.append(i)
               
        print(crosses)      
    
    def checkCutPointofObject(ObjCheck,fname1,fname2) :
        # รับ Input เป็น array
        crosses = []
        # for i in range(1, len(arrayFast)):
        #     if (arrayFast[i-1] < arraySlow[i-1] and arrayFast[i] > arraySlow[i]) or \
        #     (arrayFast[i-1] > arraySlow[i-1] and arrayFast[i] < arraySlow[i]):
        #        crosses.append(i)
        for i in range(1, len(ObjCheck)):
            if (ObjCheck[i-1]['buffer1'] < ObjCheck[i-1]['buffer2'] ) and \
               ( ObjCheck[i]['buffer1'] > ObjCheck[i]['buffer2'] ) :
                crosses.append('CutToUp') 
            
            if (ObjCheck[i-1]['buffer1'] > ObjCheck[i-1]['buffer2'] ) and \
               ( ObjCheck[i]['buffer1'] < ObjCheck[i]['buffer2'] ) :
                crosses.append('CutToDown')    
        print(crosses)          
         
        
           
    def getCHATGPT_Indy(self,open_prices , high_prices , low_prices ,  close_prices):
        # คำนวณค่า HLC3
        hlc3 = (high_prices + low_prices + close_prices) / 3
        # คำนวณค่า OHLC4
        OHLC4 = (open_prices + high_prices + low_prices +  close_prices) / 4
        # คำนวณค่า HLCC4
        hlcc4  = (high_prices + low_prices + close_prices +close_prices /4)
        # คำนวณค่า hml (High-Median-Low 3-point average):
        # คำนวณค่า Median
        median_price = talib.MEDPRICE(high_prices, low_prices)
        # คำนวณค่า HML (High-Median-Low 3-point average)        
        hml =  (high_prices+ median_price + low_prices / 3)
        
        # คำนวณค่า  True Range        
        # ใช้ฟังก์ชัน TRANGE ของ ta-lib ในการคำนวณค่า True Range
        tr = talib.TRANGE(high_prices, low_prices, close_prices)
        
        # คำนวณค่า SMA ของ HLC3 ด้วย period 3
        sma_hlc3 = talib.SMA(hlc3, timeperiod=3)
        
        
        
        MaFast_period = 2
        MaValue = 'hlc3'
        MaSlow_period = 34
        Signal_period = 5
        # คำนวณค่า SMA ของ HLC3 ด้วย period 3
        smaFast = talib.SMA(hlc3, timeperiod=MaFast_period)
        smaSlow = talib.SMA(hlc3, timeperiod=MaSlow_period)
        buffer1 = smaFast - smaSlow #array 
        buffer2 = talib.WMA(buffer1, Signal_period) # array
        buffer1 = np.nan_to_num(buffer1, nan=0.0)
        buffer2 = np.nan_to_num(buffer2, nan=0.0)
        return buffer1,buffer2
        
    
    def CalDegrees(StartPoint,EndPoint) :

     # คำนวณหา องศาระหว่าง 2 จุด    
        delta_y = EndPoint - StartPoint
        # ระยะห่างในแนว x (ระหว่างแท่งเทียนสองแท่งติดกัน)
        delta_x = 1
        # คำนวณมุมใน radians
        angle_radians = math.atan(delta_y / delta_x)
        # แปลงมุมจาก radians เป็น degrees
        angle_degrees = math.degrees(angle_radians) *10000
        print('**********************************')
        # print(f"Angle in radians: {angle_radians}")
        print('Start-End Point : ', StartPoint, ' :: ',EndPoint )
        print(f"Angle in degrees: {angle_degrees}")
        
        return angle_radians,angle_degrees
    

    def CalClose2FronDegrees(StartPoint,Degrees):
    
        print('***************  Step2 **************************')
        # ราคาปิดแท่งแรก
        close_1 = StartPoint
        # มุมใน degrees
        angle_degrees = Degrees

        # แปลงมุมจาก degrees เป็น radians
        angle_radians = math.radians(angle_degrees)

        # คำนวณการเปลี่ยนแปลงของราคาปิด (Delta y)
        delta_y = math.tan(angle_radians)

        # คำนวณราคาปิดของแท่งเทียนถัดไป
        close_2 = close_1 + delta_y

        print(f"Close 1: {close_1}")
        print(f"Angle: {angle_degrees} degrees")
        print(f"Close 2: {close_2}")
    
        return close_2    

      # Parse JSON string with custom parse_float function
    def custom_parse_float(self,value):
        try:
            return float(value)
        except OverflowError:
           return value
    
    def getNewCandle(self) :
        # JSON ต้นแบบ
        json_data = '''
        {
            "curpair": "",  
            "dataMultiply" : 1000000,
            "candleCode": "",
            "datecandle" : "",
            "minuteno": "",
            "MaxGreenCon" : 0,
            "MaxRedCon" : 0,
            "MaxSidewayCon" : 0,            
            "RawData": {
                "id": 0,
                "MinuteNo" :"",
                "from": 0,
                "at": 0,
                "to": 0,
                "open": 0,
                "close": 0,
                "min": 0,
                "max": 0,
                "volume": 0
            },
            "bodyData": {
                "Color": "",
                "CandleHeight": 0.0,
                "BodyHeight": 0.0,
                "UHeight": 0.0,
                "LHeight": 0.0,
                "BodyHeightPercent": 0.0,
                "UHeightPercent": 0.0,
                "LHeightPercent": 0.0,
                "CandleType": ""
            },
            "macd": {
                "ema3": 0.0,
                "ema5": 0.0,
                "ema9": 0.0,
                "macd": 0.0,
                "signalLine": 0.0,
                "histogram": 0.0,
                "analysis": {
                    "slope3Value": 0,
                    "slopeDirection3": "",
                    "slopeDirection5": "",
                    "slopeDirection9": "",
                    "emaAbove": "3",
                    "emaConflict" : "",
                    "ConvergenceType": 0.0,
                    "ConvergenceType": "",
                    "TurnPointType": "",
                    "IdOfLastTurnPoint": "",
                    "TurnPointNo": 0,
                    "CutPointType": ""
                }
            },
            "chatgpt": {
                "buffer1" : 0,
                "buffer2" : 0,
                "diff" : 0 ,
                "LastCutPointCode" : "",
                "CutPointCode" : "",
                "CutPointContiue" : 0,
                "CutPointType" : ""
            },
            "Bollinger": {
                "upper_band" : 0,
                "middle_band" : 0,
                "lower_band" : 0
            },
            "STOCH" : {
                "slowk" : 0, 
                "slowd": 0 
            },
            "RSI": {
                "value": 0
            },
            "ATR": {
                "value": 0
            },
            "ADX": {
                "value": 0,
                "diPlus" : 0,
                "diMinus" : 0
            },
            
            "trade": [{
                "tradeno": 1,
                "action": "CALL",
                "MoneyTrade": 2,
                "profit": 0.0,
                "balance": 0.0
            }
            ]
        }
        '''
        return  json.loads(json_data)
        
    
    # def __init__(self,curpair):
    #     # data_dict = json.loads(json_data)
    #     # candle = Candle(**data_dict)
    #     self.timeinterval = 60
    #     self.curpair = curpair
    #     # self.dataMultiply = dataMultiply,
    #     self.candles = []
    #     # self.data_dict= data_dict
    
    def PostCandleListToPHP(self,AnalysisCandle)->str :
        
        AnalysisCandleString = json.dumps(AnalysisCandle)
        
        json_object = json.loads(AnalysisCandleString, parse_float=self.custom_parse_float)
        # print(json_object)
        dataJsonString  = json.dumps(json_object)
        # json_obj = json.loads(dataJsonString)
        url = 'https://lovetoshopmall.com/iqlab/SaveAnalysisData.php' 
        myobj = {       
        'Mode' : 'SaveAnalysisData' ,
        'dataPost' : dataJsonString
        }
        print('Start Post Please Wait....')
        
        
        # f = open('demofile2.json', 'a')
        # f.write(dataJsonString)
        # f.close()
        
        
        x = requests.post(url, json = myobj)
        if x.status_code == 200:
           print('Request was successful')
           print('Return Data-------> ',x.text)
        else:
           print('Request failed with status code:', x.status_code)
           # Print the error message
           print('Error message:', x.text)
        
    def getADX(self) :
        
        # ค่า ADX (Average Directional Index) ที่ได้มาบ่งบอกถึงความแรงของแนวโน้มในตลาด โดยมีการตีความดังนี้:
        #     ADX น้อยกว่า 20: บ่งบอกถึงตลาดที่ไม่มีแนวโน้มที่ชัดเจน หรืออาจเป็นช่วงที่ตลาดกำลังรอเกิดแนวโน้มใหม่
        #     ADX ระหว่าง 20 ถึง 25: บ่งบอกถึงการเริ่มต้นของแนวโน้ม อาจเป็นสัญญาณให้ระวังเตรียมตัวสำหรับการเปลี่ยนแปลงในทิศทางของตลาด
        #     ADX มากกว่า 25: บ่งบอกถึงแนวโน้มที่มีความแรง ตลาดมีแนวโน้มที่ชัดเจนและมีความน่าเชื่อถือในการตามรับเท่านั้น
        # สร้างข้อมูลราคาตัวอย่าง
        high_prices = np.random.random(100) * 100
        low_prices = np.random.random(100) * 100
        close_prices = np.random.random(100) * 100

        # คำนวณ ADX ด้วย talib
        adx = talib.ADX(high_prices, low_prices, close_prices, timeperiod=14)
        # คำนวณค่า DI+
        di_plus = talib.PLUS_DI(high_prices, low_prices, close_prices, timeperiod=14)
        # คำนวณค่า DI-
        di_minus = talib.MINUS_DI(high_prices, low_prices, close_prices, timeperiod=14)

        return adx,di_plus,di_minus
        
        
    def getICHIMoku(self,candleList) :
        import talib
        import numpy as np

        # ตัวอย่างข้อมูลราคาสูงสุด, ต่ำสุด, และปิด
        high_prices = np.array([30, 31, 29, 28, 32, 33, 31, 30, 32, 34])
        low_prices = np.array([28, 29, 27, 26, 30, 31, 29, 28, 30, 32])
        close_prices = np.array([29, 30, 28, 27, 31, 32, 30, 29, 31, 33])

        # คำนวณค่า Ichimoku Cloud ด้วย talib
        tenkan_sen = talib.MIN(high_prices, timeperiod=9) + talib.MAX(low_prices, timeperiod=9) / 2
        kijun_sen = talib.MIN(high_prices, timeperiod=26) + talib.MAX(low_prices, timeperiod=26) / 2
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        senkou_span_b = (talib.MIN(high_prices, timeperiod=52) + talib.MAX(low_prices, timeperiod=52)) / 2
        chikou_span = np.roll(close_prices, -26)

        # กำหนดค่าเลื่อนไปข้างหน้า 26 ช่วงเวลา
        senkou_span_a = np.roll(senkou_span_a, 26)
        senkou_span_b = np.roll(senkou_span_b, 26)

        # การแสดงผลค่า Ichimoku Cloud
        print(f"Tenkan-sen: {tenkan_sen}")
        print(f"Kijun-sen: {kijun_sen}")
        print(f"Senkou Span A: {senkou_span_a}")
        print(f"Senkou Span B: {senkou_span_b}")
        print(f"Chikou Span: {chikou_span}")

               
        
    def CheckCrossLine(self,Previous1,Previous2,Currentvalue1,Currentvalue2) :
        
        
        cross = 'NoCross' ;lineAbove = ''     
        convergenceType= ''    
        SlopeDirection = 'Up'    
        
        if (Previous1  < Previous2 ) and  ( Currentvalue1  > Currentvalue2 ) :
            cross = 'Cross2Up' ; lineAbove = '1'        
        
        if (Previous1  > Previous2 ) and  ( Currentvalue1  < Currentvalue2 ) :
            cross = 'Cross2Down' ; lineAbove = '2'        
        
            
        Distance  = round(abs(Currentvalue1 - Currentvalue2) * 1000*1000,2)
        PreviousDistance  = abs(Previous1-Previous2)    
        convergenceValue = Distance - PreviousDistance
        if Distance > PreviousDistance :
           convergenceType = 'divergence' 
        else :
           convergenceType = 'convergence'   
        
        SlopeValue1 = round((Currentvalue1 - Previous1 ) *1000*1000,5)
        SlopeValue2 = round((Currentvalue2 - Previous2 ) *1000*1000,5)
        if Currentvalue1 > Previous1 : 
            SlopeDirection1 = 'Slope-Up'    
        else:
            SlopeDirection1 = 'Slope-Down'       
            
        if Currentvalue2 > Previous2 : 
            SlopeDirection2 = 'Slope-Up'    
        else:
            SlopeDirection2 = 'Slope-Down'           
        
        return cross,lineAbove,convergenceValue,convergenceType,SlopeValue1,SlopeValue2,SlopeDirection1,SlopeDirection2
        
    
    def getClosePrices(self,AnalysisDataList) :
        
        close_pricesList0 = []
        for i in range(len(AnalysisDataList)):        
            close_pricesList0.append(AnalysisDataList[i]["RawData"]["close"])            
            
        close_pricesList = np.array(close_pricesList0)
        return close_pricesList
    
    def getPricesNumpy(self,AnalysisDataList,nameprice) :
        
        pricesList0 = []
        for i in range(len(AnalysisDataList)):        
            pricesList0.append(AnalysisDataList[i]["RawData"][nameprice])            
            
        pricesList = np.array(pricesList0)
        return pricesList
        
    def fillManyRawData(self,candleList)    :
        
        
        AnalysisDataList = []
        for i in range(len(candleList)) :            
            candleDict = self.getNewCandle() # ได้ DataDict กลับมา    
            candleDict['datecandle']  =  pdatetime.B2_cvTimestamp2DateStr(candleList[i]['from'])     
            candleDict['MinuteNo']  =  pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[i]['from'])
            candleDict['RawData']['id'] = candleList[i]['id']
            candleDict['RawData']['MinuteNo']  =  pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[i]['from'])
            candleDict['RawData']['from'] = candleList[i]['from']
            candleDict['RawData']['to'] = candleList[i]['to']
            candleDict['RawData']['open'] = candleList[i]['open']
            candleDict['RawData']['close'] = candleList[i]['close']
            candleDict['RawData']['min'] = candleList[i]['min']
            candleDict['RawData']['max'] = candleList[i]['max']
            candleDict['RawData']['volume'] = candleList[i]['volume']
            AnalysisDataList.append(candleDict)
        
        print('****************************************')    
        return AnalysisDataList    
            
        
        
        
    
    def fillRawData(self,candle) :
        
        RawData  =  {
            "id": candle['id'],        
            "from": candle['from'],
            "at": candle['at'],
            "to": candle['to'],
            "open": candle['open'],
            "close": candle['close'],
            "min": candle['min'],
            "max": candle['max'],
              "volume": candle['volume']
        }
        
        return RawData
    
    def AnalyzeTurnPoint(self) :
        
        if len(self.candles) >= 2 :
            index0 = len(self.candles)-3 ;index1 = len(self.candles)-2; indexCurrent = len(self.candles)-1  
            # print(self.candles[1].macd.analysis)
            # if (self.candles[index0]['macd']['ema3'] < self.candles[index1]['macd']['ema3']) and (self.candles[index1]['macd']['ema3'] > self.candles[indexCurrent]['macd']['ema3']):
            #    self.candles[index1].macd.TurnPointType = 'TurnDown'
            #    #print('TurnDown')
            
            # if (self.candles[index0].macd.ema3 > self.candles[index1].macd.ema3) and (self.candles[index1].macd.ema3 < self.candles[indexCurrent].macd.ema3):
            #    self.candles[index1].macd.TurnPointType = 'TurnUp'
            #    #print('TurnUp')
           
           
        
        
    
    def AnalyzeBody(self,candle) :
        
        # #print(candle)
        dataMultiply = 1000*1000
        pos1 = candle['RawData']['max']
        pos4 = candle['RawData']['min']
        if candle['RawData']['open'] > candle['RawData']['close'] :
           pos2 = candle['RawData']['open'] ; pos3 = candle['RawData']['close']
           color = 'Equal'
        if candle['RawData']['open'] > candle['RawData']['close'] :
           pos2 = candle['RawData']['open'] ; pos3 = candle['RawData']['close']
           color = 'Red'
        else :
           pos2 = candle['RawData']['close'] ;pos3 = candle['RawData']['open']
           color = 'Green'
                
        if (pos1-pos4) != 0 :
           bodyHeightPercent = round(((pos2-pos3)/(pos1-pos4))*100,4)
           UHeightPercent = round(((pos1-pos2)/(pos1-pos4))*100,4)
           LHeightPercent =  round(((pos3-pos4)/(pos1-pos4))*100,4)
        else :
           bodyHeightPercent = 0.001    
           UHeightPercent = 0
           LHeightPercent =  0
           
        bodyInfo =  {
            "Color": color,
            "ColorList" : '',
            "GreenCon" : 0,
            "RedCon" : 0 ,
            "SidewayCon" : 0 ,
            "CandleHeight": round(abs(pos1-pos4) * dataMultiply,5),
            "BodyHeight": round(abs(pos2-pos3) * dataMultiply,5),
            "UHeight":   round((pos1-pos2) * dataMultiply,5),
            "LHeight":  round((pos3-pos4)* dataMultiply,5),
            "BodyHeightPercent": bodyHeightPercent ,
            "UHeightPercent": UHeightPercent,
            "LHeightPercent": LHeightPercent,
            "CandleType": "???"
        }
        
        return bodyInfo 
    
    def getAnalyzeFromMACD(self,candleList,ema3,ema5) :
        
        
        lastIndex = len(candleList)-1
        emaAbove = '' ; color = '' ; emaConflict = '' 
        previousMACD = 0 ; convergenceValue = 0 ; convergenceType  = ''
        previousTurn = ''
        if lastIndex == 1 : 
           return emaAbove,emaConflict,convergenceValue,convergenceType,previousTurn
       
        if candleList[lastIndex]['close'] < candleList[lastIndex]['open'] : color = 'Red'                       
        if candleList[lastIndex]['close'] > candleList[lastIndex]['open'] : color = 'Green' 
        if candleList[lastIndex]['close'] == candleList[lastIndex]['open'] : color = 'Equal'                       
        if ema3[lastIndex] < ema5[lastIndex] : 
            emaAbove = '5Above'
            if color == 'Green' : emaConflict = '5ButGreen'
        if ema3[lastIndex] > ema5[lastIndex] : 
            emaAbove = '3Above'     
            if color == 'Red' : emaConflict = '3ButRed'
        
        if lastIndex >= 2 :
            
            index0 = lastIndex -2 ;index1 = lastIndex -1 ; indexCurrent = lastIndex
            previousMACD = ema3[index1] - ema5[index1]
            thismacd = ema3[lastIndex] - ema5[lastIndex]            
            # convergenceValue = thismacd
            convergenceValue = thismacd - previousMACD
            if  thismacd > previousMACD :
                convergenceType = 'Diver'                
            else :
                convergenceType = 'Conver'
            if (candleList[index0]['close'] < candleList[index1]['close']) and (candleList[index1]['close'] > candleList[indexCurrent]['close']):
                previousTurn = 'TurnDown' 
                
            if (candleList[index0]['close'] > candleList[index1]['close']) and (candleList[index1]['close'] < candleList[indexCurrent]['close']):
                previousTurn = 'TurnUp'     
           
        return emaAbove,emaConflict,convergenceValue,convergenceType,previousTurn
        
    def getMACD(self,indexno,candleList,fastperiod : int, slowperiod :int, signalperiod:int )  :
        
        emaAbove = ''; emaConflict = ''; convergenceValue = '';convergenceType = ''
        # macd = indicatorTALIB.CreateMACD(candleList,fastperiod,slowperiod, signalperiod)
        ema3,ema5,macd,signal,hist = indicatorTALIB.CreateMACDV2(candleList,indexno ,fastperiod,slowperiod,signalperiod)        
        lastIndex= len(ema3)-1        
        # emaAbove,emaConflict,convergenceValue,convergenceType,previousTurn = self.getAnalyzeFromMACD(candleList,ema3,ema5)        
        macd = {
        "ema3": ema3[lastIndex],
        "ema5": ema5[lastIndex],
        "ema9": ema5[lastIndex],
        "macd": macd[lastIndex],
        "signalLine": signal[lastIndex],
        "histogram": hist[lastIndex],
        "analysis": {
            "slope3Value": 0,
            "slopeDirection3": "",
            "slope5Value": 0,
            "slopeDirection5": "",
            "slopeDirection9": "",            
            "emaAbove": emaAbove,
            "emaConflict": emaConflict,
            "ConvergenceValue": convergenceValue,
            "ConvergenceType": convergenceType,
            "TurnPointType": "",
            "IdOfLastTurnPoint": "",
            "TurnPointNo": 0,
            "CutPointType": "-",
            "IdOfLastCutPoint": 0            
         }
        }
        return macd
    
    def CalSlopeValue(AnalysisDataList) :
        
        # ตัวอย่างข้อมูลราคาปิด
        # close_prices = np.array([100, 102, 105, 107, 106, 108, 110])
        
        
        close_pricesList0 = []
        for i in range(len(AnalysisDataList)):        
            close_pricesList0.append(AnalysisDataList[i]["RawData"]["close"])            
            
        close_pricesList = np.array(close_pricesList0)

        # คำนวณความชัน (Slope) ของราคาปิด
        x = np.arange(len(close_pricesList))  # ตำแหน่งของแท่งเทียนในเวลา
        slope, intercept = np.polyfit(x, close_pricesList, 1)  # คำนวณความชันด้วย polyfit

        # คำนวณมุมในหน่วย radian
        angle_radians = np.arctan(slope)

        # แปลงมุมจาก radian เป็น degree
        angle_degrees = np.degrees(angle_radians)

        print(f"Slope: {slope}")
        print(f"Angle (radians): {angle_radians}")
        print(f"Angle (degrees): {angle_degrees}")
        return angle_degrees,angle_radians 
        
        
    def getAnalyzeDataFromBrokerByNumCandle(self,brokerObj,curpair,numcandle,timeRequest) :
        
        # brokerObj เช่น I_want_money
        print('Cur Pair is', curpair)
        
        print('Time Request ',pdatetime.B22_cvTimestamp2TimeStr_NoSecond(timeRequest))
        
        candleList = brokerObj.get_candles(curpair, self.timeinterval, numcandle,timeRequest)
        print('On 8989 -->' ,(candleList[0]['from']))    
        AnalysisDataList = self.fillManyRawData(candleList)
        # print('Length Of Analysys Data = ',len(AnalysisDataList))        
        time1 = time.time()        
        close_pricesList = self.getClosePrices(AnalysisDataList)
        
        # low_pricesList = self.getClosePrices(AnalysisDataList)
        # Step-1 สร้าง ข้อมูลดิบ , macd ที่ยังไม่วิเคราะห์
        for i in range(len(AnalysisDataList)):            
            AnalysisDataList[i]['curpair'] = curpair
            # AnalysisDataList[i]['candledate'] =pdatetime.B2_cvTimestamp2DateStr(AnalysisDataList[i]['RawData']['from'])
             
            AnalysisDataList[i]['bodyData'] = self.AnalyzeBody(AnalysisDataList[i])
            fastperiod = 3 ; slowperiod= 5 ; signalperiod =4 
            # AnalysisDataList[i]['macd']  = self.getMACD(i,AnalysisDataList,fastperiod , slowperiod, signalperiod)            
            
        # Step-2 สร้าง  macd และ ข้อมูลวิเคราะห์ จากข้อมูล macd 
        # ราคาปิด
        high_prices = self.getPricesNumpy(AnalysisDataList,'max')
        low_prices = self.getPricesNumpy(AnalysisDataList,'min')
        close_prices = self.getPricesNumpy(AnalysisDataList,'close')   
        open_prices = self.getPricesNumpy(AnalysisDataList,'open')                
        # สร้าง macd
        fastperiod= 3 ;  slowperiod= 5  ; signalperiod = 4
        macd, macdsignal, macdhistogram = talib.MACD(close_prices, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        # คำนวณค่า EMA3,EMA5,EMA9
        ema3 = talib.EMA(close_prices, timeperiod=fastperiod)
        ema5 = talib.EMA(close_prices, timeperiod=slowperiod)
        ema9 = talib.EMA(close_prices, timeperiod=9)
        ema3 = np.nan_to_num(ema3, nan=0.0)
        ema3 = np.nan_to_num(ema3, nan=0.0)
        ema3 = np.nan_to_num(ema3, nan=0.0)
        
        for i in range(len(AnalysisDataList)):            
            AnalysisDataList[i]['macd'] = macd[i]
            AnalysisDataList[i]['ema3']  = ema3[i]
            AnalysisDataList[i]['ema5']  = ema5[i]
            AnalysisDataList[i]['ema9']  = ema9[i]
            AnalysisDataList[i]['signalLine']  = macdsignal[i] 
            AnalysisDataList[i]['histogram']  = macdhistogram[i] 
            # print('macd ',AnalysisDataList[i]['macd'])
            
            emaAbove = ''             
            if AnalysisDataList[i]['macd']['ema3']  > AnalysisDataList[i]['macd']['ema5'] : emaAbove = '3Above5'
            if AnalysisDataList[i]['macd']['ema3']  < AnalysisDataList[i]['macd']['ema5'] : emaAbove = '5Above3'                
            AnalysisDataList[i]['macd']['analysis']['emaAbove']  = emaAbove
        
        # สร้าง chat GPT lua script
        
        '''
        -- Define parameters
        MaFast_period = input(1, "Ma Fast period", input.integer=1, 1, 1000, 1)
        MaValue = input(5, "Ma Value", input.string_selection, inputs.titles) 
        MaSlow_period = input(34, "Ma Slow period", input.integer=34, 1, 1000, 1)
        Signal_period = input(5, "Signal period", input.integer=5, 1, 1000, 1)
        
        local titleValue = inputs[MaValue]
        smaFast = sma(titleValue, MaFast_period)
        smaSlow = sma(titleValue, MaSlow_period)
        -- Calculate the buffers
        buffer1 = smaFast - smaSlow
        buffer2 = wma(buffer1, Signal_period)
        -- Define buy and sell conditions
        buyCondition = buffer1 > buffer2 and buffer1[1] < buffer2[1]
        sellCondition = buffer1 < buffer2 and buffer1[1] > buffer2[1]

        '''
        
        
        buffer1,buffer2 = self.getCHATGPT_Indy(open_prices ,high_prices ,low_prices ,close_prices)
        for i in range(len(AnalysisDataList)):            
            AnalysisDataList[i]['chatgpt']['buffer1'] = buffer1[i]
            AnalysisDataList[i]['chatgpt']['buffer2'] = buffer2[i]
            AnalysisDataList[i]['chatgpt']['diff'] =  buffer1[i] - buffer2[i]

        
        # Step-3 สร้าง ข้อมูลวิเคราะห์ BB,RSI,STOCH,ADX,ATR                
        # กำหนดช่วงเวลาสำหรับ Bollinger Bands
            
        # คำนวณ Bollinger Bands
        upper_band, middle_band, lower_band = talib.BBANDS(close_pricesList, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        upper_band = np.nan_to_num(upper_band, nan=0)
        lower_band = np.nan_to_num(lower_band, nan=0)
        middle_band = np.nan_to_num(middle_band, nan=0)
        for i in range(len(upper_band)-1) :
            AnalysisDataList[i]['Bollinger']['upper_band']  = upper_band[i]
            AnalysisDataList[i]['Bollinger']['middle_band']  = middle_band[i]
            AnalysisDataList[i]['Bollinger']['lower_band']  = lower_band[i]            
        print('Finished Bollinger')
            
        # คำนวณ stochastic oscillator                
        slowk, slowd = talib.STOCH(high_prices, low_prices, close_prices, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        slowk = np.nan_to_num(slowk, nan=0)
        slowd = np.nan_to_num(slowd, nan=0)
        AnalysisDataList[i]['STOCH']['slowk']  = slowk[i]
        AnalysisDataList[i]['STOCH']['slowd']  = slowd[i]
        print('Finished STOCH')
            
        # คำนวณค่า RSI ด้วย TALIB
        rsi = talib.RSI(close_prices, timeperiod=14)
        rsi = np.nan_to_num(rsi, nan=0)
        for i in range(len(rsi)-1) :            
            AnalysisDataList[i]['RSI']['value']  = rsi[i]
        print('Finished RSI')    
            
        # คำนวณ Average True Range (ATR)
        atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)
        atr = np.nan_to_num(atr, nan=0)
        for i in range(len(atr)-1) :            
            AnalysisDataList[i]['ATR']['value']  = atr[i]
            
        # คำนวณ Average Directional Movement Index (ADX)
        adx = talib.ADX(high_prices, low_prices, close_prices, timeperiod=14)
        # คำนวณค่า DI+ (Positive Directional Indicator)
        plus_di = talib.PLUS_DI(high_prices, low_prices, close_prices, timeperiod=14)
        # คำนวณค่า DI- (Negative Directional Indicator)
        minus_di = talib.MINUS_DI(high_prices, low_prices, close_prices, timeperiod=14)
        adx = np.nan_to_num(adx, nan=0)
        plus_di = np.nan_to_num(plus_di, nan=0)
        minus_di  = np.nan_to_num(minus_di, nan=0)            
        for i in range(len(adx)-1) :            
            AnalysisDataList[i]['ADX']['value']  = adx[i]
            AnalysisDataList[i]['ADX']['diPlus']  = plus_di[i]
            AnalysisDataList[i]['ADX']['diMinus']  = minus_di[i]
                
        print('Finished ADX')
            
            # คำนวณ Kaufman Adaptive Moving Average (KAMA)
            # kama = talib.KAMA(close_prices, timeperiod=30)
            # kama2 = np.nan_to_num(kama, nan=-99)
            # AnalysisDataList[i]['kama'] = kama2
        
        
        #  สร้างการวิเคราะห์ 
        IdOfLastTurnPoint = 0  ; IdOfLastCutPoint = 0
        previousColor = AnalysisDataList[0]['bodyData']['Color'] 
        GreenCon = 0 ; RedCon = 0 ; SidewayCon = 0 ; ColorList = ""
        MaxGreenCon =  0 ; MaxRedCon =  0 ; MaxSidewayCon= 0
        
        for i in range(1,len(AnalysisDataList))   :            
            cross,lineAbove,convergenceValue,convergenceType,SlopeValue1,SlopeValue2,SlopeDirection1,SlopeDirection2 = self.CheckCrossLine(AnalysisDataList[i-1]['macd']['ema3'],AnalysisDataList[i-1]['macd']['ema5'],AnalysisDataList[i]['macd']['ema3'],AnalysisDataList[i]['macd']['ema5'])
            thisColor = AnalysisDataList[i]['bodyData']['Color'] 
            ColorList = ColorList + thisColor + ','
            AnalysisDataList[i]['bodyData']['ColorList']  = '' #ColorList
            if previousColor == thisColor :
               if thisColor == 'Green'  : GreenCon = GreenCon + 1 ; RedCon = 0
               if thisColor == 'Red'    : RedCon = RedCon + 1 ; GreenCon = 0
               SidewayCon = 0
               
            else: 
               if thisColor == 'Green'  : GreenCon = GreenCon+1 ; RedCon = 0
               if thisColor == 'Red'    : RedCon = RedCon + 1 ; GreenCon = 0
               SidewayCon = SidewayCon + 1
            
                
            AnalysisDataList[i]['bodyData']['GreenCon']  = GreenCon 
            AnalysisDataList[i]['bodyData']['RedCon']    = RedCon 
            AnalysisDataList[i]['bodyData']['SidewayCon']    = SidewayCon
            if GreenCon > MaxGreenCon : MaxGreenCon = GreenCon  
            if RedCon > MaxRedCon : MaxRedCon = RedCon  
            if SidewayCon > MaxSidewayCon : MaxSidewayCon = SidewayCon
               
            
            previousColor = thisColor 
            
            # print(cross,lineAbove,convergenceType,SlopeValue,SlopeDirection)
            AnalysisDataList[i]['macd']['analysis']['ConvergenceValue'] = convergenceValue
            AnalysisDataList[i]['macd']['analysis']['ConvergenceType'] = convergenceType
            AnalysisDataList[i]['macd']['analysis']['slope3Value'] = SlopeValue1
            AnalysisDataList[i]['macd']['analysis']['slope5Value'] = SlopeValue2
            AnalysisDataList[i]['macd']['analysis']['slopeDirection3'] =  SlopeDirection1
            AnalysisDataList[i]['macd']['analysis']['slopeDirection5'] =  SlopeDirection2
            AnalysisDataList[i]['macd']['analysis']['CutPointType'] =  cross
            if cross == 'Cross2Down' or cross == 'Cross2Up' :
                IdOfLastCutPoint = AnalysisDataList[i]['RawData']['id']
                AnalysisDataList[i]['macd']['analysis']['IdOfLastCutPoint'] =  IdOfLastCutPoint
            else :
                AnalysisDataList[i]['macd']['analysis']['IdOfLastCutPoint'] =  IdOfLastCutPoint    
            
            if AnalysisDataList[i]['macd']['analysis']['emaAbove'] ==  "3Above5" and  AnalysisDataList[i]['bodyData']['Color']  ==  "Red" :                  
               
               AnalysisDataList[i]['macd']['analysis']['emaConflict'] =  "3Above5 --> Red" 
            
            if AnalysisDataList[i]['macd']['analysis']['emaAbove'] ==  "5Above3" and  AnalysisDataList[i]['bodyData']['Color']  ==  "Green" :                  
               
               AnalysisDataList[i]['macd']['analysis']['emaConflict'] =  "5Above3 --> Green"    
                
            # if i >= 2 :
            # ตรวจสอบการ Turn 3 จุด APoint, BPoint,CPoint
            APoint = AnalysisDataList[i-2]['macd']['ema3']
            BPoint = AnalysisDataList[i-1]['macd']['ema3']
            CPoint = AnalysisDataList[i]['macd']['ema3']
            if (APoint < BPoint ) and (BPoint > CPoint):
                # BPoint เป็นจุด TurnDown
               AnalysisDataList[i-1]['macd']['analysis']['TurnPointType'] = 'TurnDown'        
               IdOfLastTurnPoint = AnalysisDataList[i-1]['RawData']['id']
               AnalysisDataList[i-1]['macd']['analysis']['IdOfLastTurnPoint'] =  IdOfLastTurnPoint
            if (APoint > BPoint ) and (BPoint < CPoint):
                # BPoint เป็นจุด TurnUp
               AnalysisDataList[i-1]['macd']['analysis']['TurnPointType'] = 'TurnUp'   
               IdOfLastTurnPoint = AnalysisDataList[i-1]['RawData']['id']
               AnalysisDataList[i-1]['macd']['analysis']['IdOfLastTurnPoint'] =  IdOfLastTurnPoint
             
            AnalysisDataList[i]['macd']['analysis']['IdOfLastTurnPoint'] =  IdOfLastTurnPoint
            AnalysisDataList[i]['MaxGreenCon']   = MaxGreenCon
            AnalysisDataList[i]['MaxRedCon']   = MaxRedCon
            AnalysisDataList[i]['MaxSidewayCon']   = MaxSidewayCon
        
        # สร้างการวิเคราะห์  Body,UHeight,LHeight
        AnalysisDataList = candleType.CheckCandleType(AnalysisDataList)    
        print('เสร็จสิ้นการสร้างข้อมูล ')        
           
        time2 = time.time()    
        
        
        
        print('Used Time :' , time2-time1 ,' Type ==',type(AnalysisDataList) )         
        jsonFileName = 'data7878.json'
        df = pd.DataFrame.from_dict(AnalysisDataList)                
        # Convert DataFrame to JSON
        json_data = df.to_json(orient='records')
        with open(jsonFileName, 'w') as file:
             file.write(json_data)
        
        # print('บันทึกไปที่ ',jsonFileName )
        # for i in range(len(AnalysisDataList)) :
        #     print('Loop ',i )
        #     my_dict = dict(AnalysisDataList[0])
        #     json_data = json.dumps(my_dict)
        #     with open('data.json999', 'a') as file:
        #          file.write(json_data)
          
        
        # Convert dictionary to JSON string
        # py_list = AnalysisDataList.tolist()
        # json_data = json.dumps(AnalysisDataList)
        # # Save JSON string to a file
        # with open('data999.json', 'w') as file:
        #      file.write(json_data)
        
        
        # print(AnalysisDataList[0])
        return AnalysisDataList 
    
    def getAnalyzeDataFromBrokerByCandleList(self,curpair,candleList) :
        
        # brokerObj เช่น I_want_money
        print('Cur Pair is', curpair)        
        # print('On getAnalyzeDataFromBrokerByCandleList 8989 -->' ,(candleList[0]['from']))    
        AnalysisDataList = self.fillManyRawData(candleList)
        print('Length Of Analysys Data = ',len(AnalysisDataList))        
        time1 = time.time()        
        close_pricesList = self.getClosePrices(AnalysisDataList)
        
        # low_pricesList = self.getClosePrices(AnalysisDataList)
        # Step-1 สร้าง ข้อมูลดิบ , macd ที่ยังไม่วิเคราะห์
        for i in range(len(AnalysisDataList)):            
            AnalysisDataList[i]['curpair'] = curpair
            # AnalysisDataList[i]['candledate'] =pdatetime.B2_cvTimestamp2DateStr(AnalysisDataList[i]['RawData']['from'])
             
            AnalysisDataList[i]['bodyData'] = self.AnalyzeBody(AnalysisDataList[i])
            fastperiod = 3 ; slowperiod= 5 ; signalperiod =4 
            # AnalysisDataList[i]['macd']  = self.getMACD(i,AnalysisDataList,fastperiod , slowperiod, signalperiod)            
            
        # Step-2 สร้าง ข้อมูลวิเคราะห์ จากข้อมูล macd 
        # ราคาปิด
        
        high_prices = self.getPricesNumpy(AnalysisDataList,'max')
        low_prices = self.getPricesNumpy(AnalysisDataList,'min')
        open_prices = self.getPricesNumpy(AnalysisDataList,'open')   
        close_prices = self.getPricesNumpy(AnalysisDataList,'close')   
        fastperiod= 3 ; slowperiod=5 ; signalperiod = 4
        macd, macdsignal, macdhist = talib.MACD(close_prices, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)     
        # คำนวณค่า EMA
        ema3 = talib.EMA(close_prices, timeperiod=3)
        ema5 = talib.EMA(close_prices, timeperiod=5)
        ema9 = talib.EMA(close_prices, timeperiod=6)
        ema3 = np.nan_to_num(ema3, nan=0.0)
        ema5 = np.nan_to_num(ema5, nan=0.0)
        ema9 = np.nan_to_num(ema9, nan=0.0)
        
        macd = np.nan_to_num(macd, nan=0.0)
        macdhist = np.nan_to_num(macdhist, nan=0.0)
        macdsignal = np.nan_to_num(macdsignal, nan=0.0)
        for i in range(len(AnalysisDataList)):            
            
            AnalysisDataList[i]['macd']['ema3'] = ema3[i]
            AnalysisDataList[i]['macd']['ema5'] = ema5[i]
            AnalysisDataList[i]['macd']['ema9'] = ema9[i]
            AnalysisDataList[i]['macd']['macd'] = macd[i]
            AnalysisDataList[i]['macd']['signalLine'] = macdsignal[i]
            AnalysisDataList[i]['macd']['histogram'] = macdhist[i]
            
            emaAbove = ''                         
            if AnalysisDataList[i]['macd']['ema3']  > AnalysisDataList[i]['macd']['ema5'] : emaAbove = '3Above5'
            if AnalysisDataList[i]['macd']['ema3']  < AnalysisDataList[i]['macd']['ema5'] : emaAbove = '5Above3'                
            AnalysisDataList[i]['macd']['analysis']['emaAbove']  = emaAbove
        
        
        buffer1,buffer2 = self.getCHATGPT_Indy(open_prices ,high_prices ,low_prices ,close_prices)
        LastCutPointCode = ''
        for i in range(len(AnalysisDataList)):            
            AnalysisDataList[i]['chatgpt']['buffer1'] = buffer1[i]
            AnalysisDataList[i]['chatgpt']['buffer2'] = buffer2[i]
            if i >= 1 :
               previousDiffer = AnalysisDataList[i-1]['chatgpt']['buffer1'] - AnalysisDataList[i-1]['chatgpt']['buffer2']
               thisDiffer = AnalysisDataList[i]['chatgpt']['buffer1'] - AnalysisDataList[i]['chatgpt']['buffer2']
               if previousDiffer < 0 and thisDiffer >= 0 :
                  AnalysisDataList[i]['chatgpt']['CutPointType']  = 'สถานะเส้นบน Slow->Fast(BUY-CALL)'
                  print(pdatetime.B22_cvTimestamp2TimeStr_NoSecond(AnalysisDataList[i]['RawData']['from']-120),' = ',AnalysisDataList[i]['chatgpt']['CutPointType'] )
                  AnalysisDataList[i]['chatgpt']['CutPointCode']  = 'SF'
                  LastCutPointCode = 'SF'
                  
               if previousDiffer > 0 and thisDiffer < 0 :
                  AnalysisDataList[i]['chatgpt']['CutPointType']  = 'สถานะเส้นบน Fast->Slow(SALE-PUT)'
                  print(pdatetime.B22_cvTimestamp2TimeStr_NoSecond(AnalysisDataList[i]['RawData']['from']-180+120),' = ',AnalysisDataList[i]['chatgpt']['CutPointType'] )
                  AnalysisDataList[i]['chatgpt']['CutPointCode']  = 'FS'
                  LastCutPointCode = 'FS'
               
               lastIndex = len(AnalysisDataList)-1
               
               
               
               
               AnalysisDataList[i]['chatgpt']['LastCutPointCode']  = LastCutPointCode
        
        st =  pdatetime.B22_cvTimestamp2TimeStr_NoSecond(AnalysisDataList[lastIndex-2]['RawData']['from'] )+'->'+AnalysisDataList[lastIndex-2]['chatgpt']['CutPointCode'] + ';'
        st =  st+ pdatetime.B22_cvTimestamp2TimeStr_NoSecond(AnalysisDataList[lastIndex-1]['RawData']['from'] )+'->'+AnalysisDataList[lastIndex-1]['chatgpt']['CutPointCode'] + ';'
        st =  st+ pdatetime.B22_cvTimestamp2TimeStr_NoSecond(AnalysisDataList[lastIndex]['RawData']['from'] )+'->'+AnalysisDataList[lastIndex]['chatgpt']['CutPointCode']        
        print(st)
        # Step-3 สร้าง ข้อมูลวิเคราะห์ BB,RSI,STOCH,ADX,ATR                
        # กำหนดช่วงเวลาสำหรับ Bollinger Bands
            
        # คำนวณ Bollinger Bands
        upper_band, middle_band, lower_band = talib.BBANDS(close_pricesList, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        upper_band = np.nan_to_num(upper_band, nan=0)
        lower_band = np.nan_to_num(lower_band, nan=0)
        middle_band = np.nan_to_num(middle_band, nan=0)
        for i in range(len(upper_band)-1) :
            AnalysisDataList[i]['Bollinger']['upper_band']  = upper_band[i]
            AnalysisDataList[i]['Bollinger']['middle_band']  = middle_band[i]
            AnalysisDataList[i]['Bollinger']['lower_band']  = lower_band[i]            
        # print('Finished Bollinger')
            
        # คำนวณ stochastic oscillator                
        slowk, slowd = talib.STOCH(high_prices, low_prices, close_prices, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        slowk = np.nan_to_num(slowk, nan=0)
        slowd = np.nan_to_num(slowd, nan=0)
        AnalysisDataList[i]['STOCH']['slowk']  = slowk[i]
        AnalysisDataList[i]['STOCH']['slowd']  = slowd[i]
        # print('Finished STOCH')
            
        # คำนวณค่า RSI ด้วย TALIB
        rsi = talib.RSI(close_prices, timeperiod=14)
        rsi = np.nan_to_num(rsi, nan=0)
        for i in range(len(rsi)-1) :            
            AnalysisDataList[i]['RSI']['value']  = rsi[i]
        # print('Finished RSI')    
            
        # คำนวณ Average True Range (ATR)
        atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)
        atr = np.nan_to_num(atr, nan=0)
        for i in range(len(atr)-1) :            
            AnalysisDataList[i]['ATR']['value']  = atr[i]
            
        # คำนวณ Average Directional Movement Index (ADX)
        timeperiod = 7
        adx = talib.ADX(high_prices, low_prices, close_prices, timeperiod)
        lastIndex = len(adx)-1
        
        # print('ความยาว ADX = ' , len(adx) , ' Lastvalue=',adx[lastIndex])
        # print('adx =',adx[lastIndex])
        # print('adx =',adx[lastIndex-1])
        # print('adx =',adx[lastIndex-2])
        # print('adx =',adx[lastIndex-3])
        # print(adx)
        
        # คำนวณค่า DI+ (Positive Directional Indicator)
        plus_di = talib.PLUS_DI(high_prices, low_prices, close_prices, timeperiod)
        # คำนวณค่า DI- (Negative Directional Indicator)
        minus_di = talib.MINUS_DI(high_prices, low_prices, close_prices, timeperiod)
        adx = np.nan_to_num(adx, nan=0)
        plus_di = np.nan_to_num(plus_di, nan=0)
        minus_di  = np.nan_to_num(minus_di, nan=0)            
        for i in range(0,len(adx)) :            
            AnalysisDataList[i]['ADX']['value']  = adx[i]
            AnalysisDataList[i]['ADX']['diPlus']  = plus_di[i]
            AnalysisDataList[i]['ADX']['diMinus']  = minus_di[i]
                
        # print('Finished ADX Len adx=',len(adx) )
            
            # คำนวณ Kaufman Adaptive Moving Average (KAMA)
            # kama = talib.KAMA(close_prices, timeperiod=30)
            # kama2 = np.nan_to_num(kama, nan=-99)
            # AnalysisDataList[i]['kama'] = kama2
        
        
        #  สร้างการวิเคราะห์ 
        IdOfLastTurnPoint = 0  ; IdOfLastCutPoint = 0
        previousColor = AnalysisDataList[0]['bodyData']['Color'] 
        GreenCon = 0 ; RedCon = 0 ; SidewayCon = 0 ; ColorList = ""
        MaxGreenCon =  0 ; MaxRedCon =  0 ; MaxSidewayCon= 0
        
        for i in range(1,len(AnalysisDataList))   :            
            cross,lineAbove,convergenceValue,convergenceType,SlopeValue1,SlopeValue2,SlopeDirection1,SlopeDirection2 = self.CheckCrossLine(AnalysisDataList[i-1]['macd']['ema3'],AnalysisDataList[i-1]['macd']['ema5'],AnalysisDataList[i]['macd']['ema3'],AnalysisDataList[i]['macd']['ema5'])
            thisColor = AnalysisDataList[i]['bodyData']['Color'] 
            ColorList = ColorList + thisColor + ','
            AnalysisDataList[i]['bodyData']['ColorList']  = '' #ColorList
            if previousColor == thisColor :
               if thisColor == 'Green'  : GreenCon = GreenCon + 1 ; RedCon = 0
               if thisColor == 'Red'    : RedCon = RedCon + 1 ; GreenCon = 0
               SidewayCon = 0
               
            else: 
               if thisColor == 'Green'  : GreenCon = GreenCon+1 ; RedCon = 0
               if thisColor == 'Red'    : RedCon = RedCon + 1 ; GreenCon = 0
               SidewayCon = SidewayCon + 1
            
                
            AnalysisDataList[i]['bodyData']['GreenCon']  = GreenCon 
            AnalysisDataList[i]['bodyData']['RedCon']    = RedCon 
            AnalysisDataList[i]['bodyData']['SidewayCon']    = SidewayCon
            if GreenCon > MaxGreenCon : MaxGreenCon = GreenCon  
            if RedCon > MaxRedCon : MaxRedCon = RedCon  
            if SidewayCon > MaxSidewayCon : MaxSidewayCon = SidewayCon
               
            
            previousColor = thisColor 
            
            # print(cross,lineAbove,convergenceType,SlopeValue,SlopeDirection)
            AnalysisDataList[i]['macd']['analysis']['ConvergenceValue'] = convergenceValue
            AnalysisDataList[i]['macd']['analysis']['ConvergenceType'] = convergenceType
            AnalysisDataList[i]['macd']['analysis']['slope3Value'] = SlopeValue1
            AnalysisDataList[i]['macd']['analysis']['slope5Value'] = SlopeValue2
            AnalysisDataList[i]['macd']['analysis']['slopeDirection3'] =  SlopeDirection1
            AnalysisDataList[i]['macd']['analysis']['slopeDirection5'] =  SlopeDirection2
            AnalysisDataList[i]['macd']['analysis']['CutPointType'] =  cross
            if cross == 'Cross2Down' or cross == 'Cross2Up' :
                IdOfLastCutPoint = AnalysisDataList[i]['RawData']['id']
                AnalysisDataList[i]['macd']['analysis']['IdOfLastCutPoint'] =  IdOfLastCutPoint
            else :
                AnalysisDataList[i]['macd']['analysis']['IdOfLastCutPoint'] =  IdOfLastCutPoint    
            
            if AnalysisDataList[i]['macd']['analysis']['emaAbove'] ==  "3Above5" and  AnalysisDataList[i]['bodyData']['Color']  ==  "Red" :                  
               
               AnalysisDataList[i]['macd']['analysis']['emaConflict'] =  "3Above5 --> Red" 
            
            if AnalysisDataList[i]['macd']['analysis']['emaAbove'] ==  "5Above3" and  AnalysisDataList[i]['bodyData']['Color']  ==  "Green" :                  
               
               AnalysisDataList[i]['macd']['analysis']['emaConflict'] =  "5Above3 --> Green"    
                
            # if i >= 2 :
            # ตรวจสอบการ Turn 3 จุด APoint, BPoint,CPoint
            APoint = AnalysisDataList[i-2]['macd']['ema3']
            BPoint = AnalysisDataList[i-1]['macd']['ema3']
            CPoint = AnalysisDataList[i]['macd']['ema3']
            if (APoint < BPoint ) and (BPoint > CPoint):
                # BPoint เป็นจุด TurnDown
               AnalysisDataList[i-1]['macd']['analysis']['TurnPointType'] = 'TurnDown'        
               IdOfLastTurnPoint = AnalysisDataList[i-1]['RawData']['id']
               AnalysisDataList[i-1]['macd']['analysis']['IdOfLastTurnPoint'] =  IdOfLastTurnPoint
            if (APoint > BPoint ) and (BPoint < CPoint):
                # BPoint เป็นจุด TurnUp
               AnalysisDataList[i-1]['macd']['analysis']['TurnPointType'] = 'TurnUp'   
               IdOfLastTurnPoint = AnalysisDataList[i-1]['RawData']['id']
               AnalysisDataList[i-1]['macd']['analysis']['IdOfLastTurnPoint'] =  IdOfLastTurnPoint
             
            AnalysisDataList[i]['macd']['analysis']['IdOfLastTurnPoint'] =  IdOfLastTurnPoint
            AnalysisDataList[i]['MaxGreenCon']   = MaxGreenCon
            AnalysisDataList[i]['MaxRedCon']   = MaxRedCon
            AnalysisDataList[i]['MaxSidewayCon']   = MaxSidewayCon
        
        # สร้างการวิเคราะห์  Body,UHeight,LHeight
        AnalysisDataList = candleType.CheckCandleType(AnalysisDataList)    
        # print('เสร็จสิ้นการสร้างข้อมูล ')        
           
        time2 = time.time()    
        
        
        
        # print('Used Time :' , time2-time1 ,' Type ==',type(AnalysisDataList) )         
        jsonFileName = 'data7878.json'
        df = pd.DataFrame.from_dict(AnalysisDataList)                
        # Convert DataFrame to JSON
        json_data = df.to_json(orient='records')
        with open(jsonFileName, 'w') as file:
             file.write(json_data)
        
        # print('บันทึกไปที่ ',jsonFileName )
        # for i in range(len(AnalysisDataList)) :
        #     print('Loop ',i )
        #     my_dict = dict(AnalysisDataList[0])
        #     json_data = json.dumps(my_dict)
        #     with open('data.json999', 'a') as file:
        #          file.write(json_data)
          
        
        # Convert dictionary to JSON string
        # py_list = AnalysisDataList.tolist()
        # json_data = json.dumps(AnalysisDataList)
        # # Save JSON string to a file
        # with open('data999.json', 'w') as file:
        #      file.write(json_data)
        
        
        # print(AnalysisDataList[0])
        return AnalysisDataList 
    
    def add_candle(self, candle):
        self.candles.append(candle)

    def get_candle(self, index):
        return self.candles[index]

    def get_all_candles(self):
        return self.candles

    def remove_candle(self, index):
        del self.candles[index]

    def clear_all_candles(self):
        self.candles = []

# # สร้างอินสแตนซ์ของคลาส CandleArray
# candle_array = CandleArray()

# # เพิ่ม Candle เข้าไปใน array
# candle_array.add_candle(Candle(**data_dict))
# candle_array.add_candle(Candle(**data_dict))

