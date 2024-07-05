import json,sys
from declareglobal import *

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
import requests
from iqoptionapi.stable_api import IQ_Option 
import mylib  
import time
import pdatetime 
    
         
# print(curpairList[1],curpairList[2])        
# sys.exit(0)
    

curpair = 'EURUSD-OTC'
numcandle = 300
dataMultiply = 1000 * 1000
buyno = 0 ; Money =1  ; expirations_mode =1  ; profitList = [] 
balance = 0 

I_want_money = mylib.loginIQ() 
timeserver = mylib.getiqservertimestamp(I_want_money)

time1 = time.time()


data_dict = json.loads(json_data)
candle = Candle(**data_dict)

# สร้างอินสแตนซ์ของคลาส CandleArray

candle_array = CandleArray(curpair)
candleListAnalyzed = candle_array.getAnalyzeDataFromBroker(I_want_money,curpair,numcandle,timeserver)

From = candleListAnalyzed[0]['RawData']['from']
# print(' 1 Data From :',pdatetime.B22_cvTimestamp2TimeStr_NoSecond(From) )
# print(type(candleList))
time2 = time.time()
# print('Length = ', len(candleListAnalyzed))
# print(candleList[3]['bodyData'])
# print(candleList[4]['bodyData'])

# print('Time1 = ', time1, ' = ' ,pdatetime.B2_cvTimestamp2TimeStr(time1))
# print('Time2 = ', time2, ' = ' ,pdatetime.B2_cvTimestamp2TimeStr(time1))
# print('Used Time = ' , time2-time1)

currentAction = 'CALL'
# โพสไปยัง url = 'https://lovetoshopmall.com/iqlab/SaveAnalysisData.php' 
# ข้อมูลถูกบันทึกไปยัง Table-> 'RawData','bodyData','RSI','ADX','trade','STOCH','Bollinger','macd'

candle_array.PostCandleListToPHP(candleListAnalyzed)
sys.exit(0)
for i in range(0,4):
    checkbuy, id = I_want_money.buy(Money, curpair, currentAction,expirations_mode)                    
    if checkbuy == False :
       print('Buy Fail ',curpair)    
       sys.exit(0) 
    else :             
        print('*******************  Buy No =',buyno ,' MoneyTrade=',Money ,' *******************')
        candleList= candle_array.getAnalyzeDataFromBroker(I_want_money,curpair,numcandle,timeserver)
        print('Type ===> ', type(candleList))
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
