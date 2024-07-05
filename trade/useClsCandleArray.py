import json,sys
# from declareglobal import *
import mylib
import pandas as pd

from clsCandle import Candle,json_data 
# clsCandle จะทำหน้าที่ สร้าง Object ต้นแบบที่เก็บค่าข้อมูลของแท่งเทียนนั้นๆ ประกอปไปด้วย 
# RawData,bodyData,macd,macd.analysis,Bollinger,RSI,ATR,trade

from clsCandleArray import CandleArray
# CandleArray เป็น class มีหน้าที่ สร้าง Object ในแบบเดียวกับ clsCandle 
# CandleArray->getAnalyzeDataFromBroker จะได้ array ของ Candle ที่เก็บ ข้อมูลดิบ+ข้อมูลวิเคราะห์ของ candle เอาไว้
#  getAnalyzeDataFromBroker->ทำหน้าที่ 
#    brokerObj.get_candles->ดึงข้อมูลดิบจาก Broker
#    getClosePrices(AnalysisDataList)->สร้าง numpy array ของราคา close price
#    getMACD->Loop สร้างข้อมูล ema3,ema5,macd,signal,hist ด้วย indicatorTALIB.CreateMACDV2 จะได้เส้น ema3,ema5,macd
#    สร้าง  ฺBollinger Band,Stichastics,RSI,ADX,ATR 
#    candleType.CheckCandleType จำแนกชนิดของ Candle
#    Loop array สร้างข้อมูลวิเคราะห์ จาก macd ที่ได้

#  ถ้าต้องการเพิ่ม Indicator ให้เข้าไปแก้ ที่ getAnalyzeDataFromBroker

# *****************  วิธีใช้ มี 2 แบบ *************************
#  1.เก็บข้อมูล History เอาไปวิเคราะห์ โดยระบุ ช่วงวันที่ 
#  2.เก็บข้อมูล  เอาไปวิเคราะห์ โดยระบุ timserver+numcandle

import requests
from iqoptionapi.stable_api import IQ_Option 
import mylib  
import time
import pdatetime 
    
         
# print(curpairList[1],curpairList[2])        
# sys.exit(0)
def CheckCurpairOpen():
   all_assets = I_want_money.get_all_open_time()

   # ตรวจสอบคู่เงินที่เปิดให้เทรดในขณะนี้
   for asset_type, assets in all_assets.items():
    if asset_type == 'binary':
        for asset, data in assets.items():
            if data['open']:
                print(f"Asset: {asset} is open for trading")
   
   return all_assets

def getCandleHistory(curpair: str ) :
    
    # ดึงข้อมูลจาก IQ ตามวันเวลาที่กำหนด และ นำไปสร้างข้อมูล Indy ต่างๆ แล้ว Post->mysql
    # Input = Data จาก IQ-Option
    # OutPut = candleListAnalyzed(DataDict), 
    # php
    # OutPut = mysql Table = RawData,bodyData,macd,Bollinger,RSI,ADX,ATR,STOCH
    
    useCase = 'now'
    useCase = 'Interval'
    curpair = 'EURUSD-OTC'
    curpair = 'EURUSD'
    if useCase == 'Interval' :
       StartDatetimeString  = '13/06/24 15:00:00'    
       EndDatetimeString = '13/06/24 16:34:00'    
       
       StartDatetimeString  = '06/13/24 15:00:00'    
       EndDatetimeString = '06/13/24 16:34:00'    
       # ดึงข้อมูลดิบจาก IQ ข้อมูลดั้งเดิมเลย
       candle = mylib.getCandleByStartDateString(I_want_money, curpair, StartDatetimeString ,EndDatetimeString) 
    else :
       servertimestamp = mylib.getiqservertimestamp(I_want_money)
       timeinterval = 60 
       numcandle = 60
       # ดึงข้อมูลดิบจาก IQ ได้ ข้อมูลดั้งเดิมเลย
       candle = I_want_money.get_candles(curpair, timeinterval, numcandle, servertimestamp)
     
    
    
    
    startTimeCandle = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candle[0]['from'])
    stopTimeCandle = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candle[len(candle)-1]['from'])
    print('จำนวนแท่งเทียน =',len(candle) , ' Time =',startTimeCandle, ' ถึง ' ,stopTimeCandle )

    
    # candle_array = CandleArray(curpair)
    # candleListAnalyzed = candle_array.getAnalyzeDataFromBroker(I_want_money,curpair,numcandle,timeserver)
   #  print('Time Server = ', pdatetime.B22_cvTimestamp2TimeStr_NoSecond(timeserver))

    
    candle_array = CandleArray(curpair)
    candleListAnalyzed = candle_array.getAnalyzeDataFromBrokerByCandleList(curpair,candle)

   #  print('จำนวนข้อมูล  = ', len(candleListAnalyzed))
    # บันทึกไปยัง server 
    candle_array.PostCandleListToPHP(candleListAnalyzed) 
    
    balance= 0 ;winList =''
    
    lastIndex= len(candleListAnalyzed)-1
    adxValue = candleListAnalyzed[lastIndex]['ADX']['value'] 
    pointCode = candleListAnalyzed[lastIndex]['chatgpt']['LastCutPointCode'] 
    buffer1 = candleListAnalyzed[lastIndex]['chatgpt']['buffer1'] 
    buffer2 = candleListAnalyzed[lastIndex]['chatgpt']['buffer2'] 
    diff = buffer1 - buffer2 
    print(buffer1,' vs', buffer2 , ' Diff = ',diff)
    
    if pointCode == 'SF':
       currentAction = 'CALL'
    if pointCode == 'FS':
       currentAction = 'PUT'
   
    CutPointType = candleListAnalyzed[lastIndex]['chatgpt']['CutPointType'] 
    print('PointCode =',pointCode,' Desc = ', CutPointType, ' ADX VALUE=',adxValue )
    checkbuy, id = I_want_money.buy(Money, curpair, currentAction,expirations_mode)                    
    if checkbuy == False :
       print('Buy Fail ',curpair)    
       sys.exit(0) 
    else :             
        print('*******************  Buy No =',buyno ,' MoneyTrade=',Money ,' Action=',currentAction ,' *******************')
        # candleList= candle_array.getAnalyzeDataFromBroker(I_want_money,curpair,numcandle,timeserver)        
      #   AnalyzedDataList = candle_array.getAnalyzeDataFromBrokerByNumCandle(I_want_money,curpair,numcandle,timeserver)        
        profit = I_want_money.check_win_v3(id)    
        print('Profit =',profit)
      #   sys.exit(0)
        for i in range(2,20) :
            candle = I_want_money.get_candles(curpair, timeinterval, numcandle, servertimestamp)
            candleListAnalyzed = candle_array.getAnalyzeDataFromBrokerByCandleList(curpair,candle)
            lastIndex= len(candleListAnalyzed)-1
            adxValue = candleListAnalyzed[lastIndex]['ADX']['value'] 
            pointCode = candleListAnalyzed[lastIndex]['chatgpt']['LastCutPointCode'] 
            buffer1 = candleListAnalyzed[lastIndex]['chatgpt']['buffer1'] 
            buffer2 = candleListAnalyzed[lastIndex]['chatgpt']['buffer2'] 
            diff = buffer1 - buffer2 
            
            if pointCode == 'SF':
               currentAction = 'CALL'
            if pointCode == 'FS':
               currentAction = 'PUT'
            
            if diff > 0 :
               currentAction = 'CALL'
            else :
               currentAction = 'PUT'   
            
            print(buffer1,' vs', buffer2 , ' Diff = ',diff,  ' action =' ,currentAction)
            checkbuy, id = I_want_money.buy(Money, curpair, currentAction,expirations_mode)
            servertimestamp = servertimestamp +60
            print('Trade ครั้งที่  ',i,'Action =', currentAction, ' pointCode= ',pointCode,' ADX=',adxValue,' Balance=',balance)
            profit = I_want_money.check_win_v3(id) 
            if profit > 0 :
               print('Win')   
               winList = winList+ 'Win,'
            else :
               print('Loss')   
               winList = winList+ 'Loss,'
            balance = balance + profit 
            print('Trade ครั้งที่  ',i,'Profit =',profit, ' Balance= ',balance,' WinList=',winList)
       
    pass

def getCandleForTradeNow(curpair: str ,numcandle:int , timeserver) :
    
    # ดึงข้อมูลจาก IQ ตามวันเวลาที่กำหนด และ นำไปสร้างข้อมูล Indy ต่างๆ แล้ว Post->mysql
    # Input = Data จาก IQ-Option
    # OutPut = candleListAnalyzed(DataDict), 
    # php
    # OutPut = mysql Table = RawData,bodyData,macd,Bollinger,RSI,ADX,ATR,STOCH
    
    # ดึงข้อมูลดิบจาก IQ ข้อมูลดั้งเดิมเลย
    candle = mylib.getCandle(I_want_money, curpair, numcandle,timeserver)
    
    startTimeCandle = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candle[0]['from'])
    stopTimeCandle = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candle[len(candle)-1]['from'])
    print('จำนวนแท่งเทียน =',len(candle) , ' Time =',startTimeCandle, ' ถึง ' ,stopTimeCandle )

    timeserver = mylib.getiqservertimestamp(I_want_money)
    # candle_array = CandleArray(curpair)
    # candleListAnalyzed = candle_array.getAnalyzeDataFromBroker(I_want_money,curpair,numcandle,timeserver)
    print('Time Server = ', pdatetime.B22_cvTimestamp2TimeStr_NoSecond(timeserver))


    candle_array = CandleArray(curpair)
    candleListAnalyzed = candle_array.getAnalyzeDataFromBrokerByCandleList(curpair,candle)
    
    
    print('จำนวนข้อมูล  = ', len(candleListAnalyzed)) 
    lastindex=  len(candleListAnalyzed)-1
    
    print('adx ตัวสุดท้าย ',candleListAnalyzed[lastindex]['ADX']['value'])
    # print(candleListAnalyzed[lastindex-1]['ADX']['value'])
    # print(candleListAnalyzed[lastindex-2]['ADX']['value'])
    # print(candleListAnalyzed[lastindex-3]['ADX']['value'])
    # print(candleListAnalyzed[lastindex]['ADX']['VALUE'])
    # candle_array.PostCandleListToPHP(candleListAnalyzed)
    return candleListAnalyzed
    

    

curpair = 'EURUSD-OTC'
numcandle = 300
dataMultiply = 1000 * 1000
buyno = 0 ; Money =1  ; expirations_mode =1  ; profitList = [] 
balance = 0 

I_want_money = mylib.loginIQ() 

Mode= 'GetHistory'
# Mode= 'GetTrade'

numcandle = 70
timeserver = mylib.getiqservertimestamp(I_want_money)
# candleListAnalyzed = getCandleForTradeNow(curpair,numcandle,timeserver) 
if Mode == 'GetHistory' :
   # หรือ ถ้าจะดีงข้อมูลไปเก็บ 
   # เข้าไปกำหนดช่วงวันที่ ใน getCandleHistory     
   getCandleHistory(curpair)
   sys.exit(0)



timeserver = mylib.getiqservertimestamp(I_want_money)
numcandle = 60



data_dict = json.loads(json_data)
candle = Candle(**data_dict)

# สร้างอินสแตนซ์ของคลาส CandleArray

candle_array = CandleArray(curpair)
# candleListAnalyzed = candle_array.getAnalyzeDataFromBroker(I_want_money,curpair,numcandle,timeserver)
# getAnalyzeDataFromBrokerByCandleList(self,curpair,candleList)
# From = candleListAnalyzed[0]['RawData']['from']
# print(' 1 Data From :',pdatetime.B22_cvTimestamp2TimeStr_NoSecond(From) )
# print(type(candleList))


currentAction = 'CALL'
curpair = 'EURUSD-OTC'
# โพสไปยัง url = 'https://lovetoshopmall.com/iqlab/SaveAnalysisData.php' 
# ข้อมูลถูกบันทึกไปยัง Table-> 'RawData','bodyData','RSI','ADX','trade','STOCH','Bollinger','macd','chatgpt'
timeinterval = 60 ; numcandle = 60
servertimestamp = I_want_money.get_server_timestamp()
candleList = I_want_money.get_candles(curpair, timeinterval, numcandle, servertimestamp)
print('Len=',len(candleList))
if len(candleList) == 0 :
   print('No Data Len=',len(candleList), ' AT Time ',pdatetime.B22_cvTimestamp2TimeStr_NoSecond(servertimestamp))
   sys.exit(0)
   
candleListAnalyzed =  candle_array.getAnalyzeDataFromBrokerByCandleList(curpair,candleList)
# candleListAnalyzed = candle_array.getAnalyzeDataFromBrokerByNumCandle(I_want_money,curpair,numcandle,timeserver)        

candle_array.PostCandleListToPHP(candleListAnalyzed)
jsonFileName = 'data7878.json'
df = pd.DataFrame.from_dict(candleListAnalyzed)                
#  Convert DataFrame to JSON
json_data = df.to_json(orient='records')
with open(jsonFileName, 'w') as file:
    file.write(json_data)
        
# print('บันทึกไปที่ ',jsonFileName )


sys.exit(0)
for i in range(0,4):
    checkbuy, id = I_want_money.buy(Money, curpair, currentAction,expirations_mode)                    
    if checkbuy == False :
       print('Buy Fail ',curpair)    
       sys.exit(0) 
    else :             
        print('*******************  Buy No =',buyno ,' MoneyTrade=',Money ,' *******************')
        # candleList= candle_array.getAnalyzeDataFromBroker(I_want_money,curpair,numcandle,timeserver)        
        AnalyzedDataList = candle_array.getAnalyzeDataFromBrokerByNumCandle(I_want_money,curpair,numcandle,timeserver)        
        profit = I_want_money.check_win_v3(id)
        profitList.append(round(profit,2))
        balance = balance + profit 
        print('BuyNo :: ', buyno ,' Profit = ', profit , ' Balance= ',balance)
        buyno = buyno + 1





# ระบุประเภทของแท่งเทียนทั้งหมดในชุดข้อมูล

# print(candleList[10]['macd'])
# print(candleList[12])

# print(candleList[2].macd)
# FromMinute=  pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[0].from)
# print(FromMinute)
# candle_array.add_candle(Candle(**data_dict))
# candle1 = candle_array.get_candle(0)
# print(candle1)

# CandleAnalyzeList.add_candle(clsCandle)
# CandleAnalyzeList.add_candle(candle)
# print(CandleAnalyzeList)
# candleList,wincolor,firstTime,servertime  = mylib.getCandleByFirstRound(I_want_money, curpair,  numcandle)

# data_dict = json.loads(json_data)

# # สร้างออบเจกต์จากคลาส Candle
# candle = Candle(**data_dict)
# candleList = [candle]
# # เรียกใช้งานเมธอด display_info()
# candle.setCurpair('EURUSD')
# AllCandle = []

# rawCandleList= candle.getRawData(I_want_money,timeserver,numcandle) 
# for i in range(0,5) :
#     candle = candle = Candle(**data_dict)
#     candle[i]['minuteno'] = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(rawCandleList[i]['from'])
#     AllCandle.append(candle)

# print(AllCandle)
# # print( 'Time Server = ', pdatetime.B22_cvTimestamp2TimeStr_NoSecond(timeserver))

# # candle.display_info()
# # print(candleList[0])
