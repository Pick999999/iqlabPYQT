from iqoptionapi.stable_api import IQ_Option
# import constants
import requests
import time
import json
import pandas as pd
import talib as ta
import datetime
import newutil 
import numpy as np
from talib.abstract import *
import talib
import pdatetime
from datetime import datetime
import threading
import sys 
import socket
import os 
import pygame
import pytz 



# def LineNotify(msg):
def lineNotify(message):
    payload = {"message": message}
    return _lineNotify(payload)


def notifyPicture(url):
    payload = {"message": " ", "imageThumbnail": url, "imageFullsize": url}
    return _lineNotify(payload)

def InitPyGame():
    
    pygame.init()
    my_soundFinished = pygame.mixer.Sound('applause.wav')
    my_soundError = pygame.mixer.Sound('mixkit-dog-barking-twice-1.wav')
    
    return my_soundFinished,my_soundError

def CreateFolderToday() :
    
    current_time = time.time()
    # Convert the timestamp to a struct_time object
    time_struct = time.localtime(current_time)

    # Extract the day and month from the struct_time object
    day = time_struct.tm_mday
    month = time_struct.tm_mon
    year = time_struct.tm_year 

    # print(f"Day: {day}, Month: {month}")
    Desc_folder = "dataTrade/" +  str(month)
    CreateFolder(Desc_folder)
    
    Desc_folder = "dataTrade/" + str(month) + '/' + str(day)
    CreateFolder(Desc_folder)
    
    return Desc_folder
    

def PostTrade(candleAnalyArray,tradeid) :
    
    dataJsonString  = json.dumps(candleAnalyArray)
    json_obj = json.loads(dataJsonString)
    url = 'https://lovetoshopmall.com/dataservice/saveLabTrade2.php' 
    myobj = {
    'Mode'  : 'saveLabTradeFromPython' ,
    'tradeid': tradeid,    
    'dataPost' : json_obj
    }
    # print(myobj)
    x = requests.post(url, json = myobj)
    print(x.text)
    # QMessageBox.about(self, 'Title',x.text)
    
def getAnalysisFromCandle(candleAnalysisArray) :
    
    lastIndex = len(candleAnalysisArray)-1
    minuteno = candleAnalysisArray[lastIndex]['MinuteNo']   
    color = candleAnalysisArray[lastIndex]['color']   
    SlopeDirection = candleAnalysisArray[lastIndex]['SlopeDirection']   
    SlopeValue = candleAnalysisArray[lastIndex]['SlopeValue']   
    macd = candleAnalysisArray[lastIndex]['macd']   
    emaAbove = candleAnalysisArray[lastIndex]['emaAbove']   
    cutPoint =candleAnalysisArray[lastIndex]['CutPoint']   
    cPointOccur = ''
    if lastIndex > 1 :
       TurnPoint = candleAnalysisArray[lastIndex-1]['TurnPoint']  
       if TurnPoint != '??'  :
          print('9898 C Point เกิดขึ้นแล้ว' , SlopeDirection ,' สี ' , color)
          cPointOccur = 'จุดนี้เป็น จุด C Point ' + SlopeDirection + ' สี ' + color
    else :
       TurnPoint = candleAnalysisArray[lastIndex]['TurnPoint']   
       if TurnPoint != '??'  :
          print('9899 C Point เกิดขึ้นแล้ว' , SlopeDirection, ' สี ' , color)
          cPointOccur = 'จุดนี้เป็น จุด C Point ' + SlopeDirection + ' สี ' + color
       
    isConflict = candleAnalysisArray[lastIndex]['emaConflict']   
    convergence = candleAnalysisArray[lastIndex]['convergence']   
    
    return minuteno,color,SlopeDirection,SlopeValue,macd,emaAbove,TurnPoint,isConflict,convergence,cPointOccur,cutPoint
    
        
    
    
def PrintDataForAnalysis(candleAnalysisArray,DataMultiply) :
    
    lastIndex = len(candleAnalysisArray)-1
    
    color = candleAnalysisArray[lastIndex]['color']
    macd = round(candleAnalysisArray[lastIndex]['macd'],5) * DataMultiply
    macd = candleAnalysisArray[lastIndex]['macd'] * DataMultiply
    
    emaAbove = candleAnalysisArray[lastIndex]['emaAbove']
    SlopeDirection = candleAnalysisArray[lastIndex]['SlopeDirection']
    SlopeValue = round(candleAnalysisArray[lastIndex]['SlopeValue'] *DataMultiply,2)
    convergenceType = candleAnalysisArray[lastIndex]['convergenceType']
    isConflict = candleAnalysisArray[lastIndex]['isConflict']
    
    
    isTurnPoint  = 'NoTurn' ; isCutPoint = 'NoCutPoint' 
    isEMAConflict = ''
    if lastIndex > 2 :
       isTurnPoint  =  candleAnalysisArray[lastIndex-1]['TurnPoint']
       isCutPoint  =  candleAnalysisArray[lastIndex]['isCutPoint']
       
    
    print(color,',macd=',macd,', emaabove', emaAbove, ' ,' , SlopeDirection,' :: SlopeValue=',SlopeValue ,' ลู่เข้า ?',convergenceType) 
    print('isTurn Point :' , isTurnPoint , ' isCutPoint = ',isCutPoint, ' isEMAConflict  = ',isConflict)
    
    
    
    
def CalBalanceVerMartingale(profit,balance,Money,targetmoney) :
    
    balance = balance + profit 
    if balance < targetmoney :
         if profit < 0 :
            if balance > 0 and balance  < 1 :
               stDesc = 'Case เดินเงิน = A'
               print(stDesc) 
            #    stDescAll = stDescAll + stDesc  + '\n'
               Money = 2
            else :   
               stDesc = 'Case เดินเงิน = B'
               print(stDesc) 
            #    ; stDescAll = stDescAll + stDesc  + '\n'
               Money = abs(int(balance * 2 ))
         else :
            stDesc = 'Case เดินเงิน = C'
            print(stDesc) 
            # ; stDescAll = stDescAll + stDesc  + '\n'
            Money = Money  * 2  
            
         if Money <= 0 : 
            Money = 1      
    
    return Money,balance


def GenAnalysisCandle2Code(CandleArray):
    # รหัสต่างๆ 
    # 1.Color มี 3 ค่า R,G,E
    # 2.EMADirection มี 3 ค่า  U1,U2,U3,D1,D2,D3,P(Pararell)
    # 3.MACD มี 3 ค่า  P1,P2,P3,N1,N2,N3,P(Pararell)
    # 4.Convergence มี 3 ค่า C,D,E
    # 5.EMAAbove มี 2 ค่า 3,5
    # 6.isConflict มี 2 ค่า Y,N
    # 7.TurnPointType  มี 2 ค่า  TD(Turn To Down Trend),TUP (Turn To Up Trend)
    # 8.isBPoint  มี 2 ค่า R,G,'N' (ดูจากแท่งก่อนหน้าเป็น TurnPoint ?)
    # 9.isCutPoint มี 2 ค่า CD(Cut To Down Trend),CU(Cut To Up Trend)
    # 10.LastCutPoint เป็นตัวเลข
    # 11.Body
    
    lastIndex = len(CandleArray)-1
    ColorCode =  CandleArray[lastIndex]['color'] 
    macdcode = 'macd???-'
    
    EMADirection_Code=  CandleArray[lastIndex]['SlopeDirection']
    macd1 =  CandleArray[lastIndex]['macd']
    if macd1 > 0 : 
       # Up Trend 
       if macd1 >= 0 and macd1 <= 5 :
        macdcode = 'P0' 
       if macd1 > 5  and macd1 <= 10 :
        macdcode = 'P1'    
       if macd1 > 10  and macd1 <= 20 :
        macdcode = 'P2'    
       if macd1 > 30 and macd1 < 50  :
        macdcode = 'N'    
       if macd1 > 50  :
        macdcode = 'SU'       # Super MACD 
    else : 
       # Down Trend      
       macd2 = abs(macd1)    
       if macd2 >= 0 and macd2 <= 5 :
        macdcode = 'DP' 
       if macd2 > 5  and macd2 <= 10 :
        macdcode = 'D1'    
       if macd2 > 10  and macd2 <= 20 :
        macdcode = 'D2'    
       if macd2 > 30 and macd2 < 50  :
        macdcode = 'DN'    
       if macd2 > 50  :
        macdcode = 'SD'       # Super MACD 
    
    convergenceType = '??'    
    convergenceType =  CandleArray[lastIndex]['convergenceType']    
        
    candleCode = ColorCode + '-' + EMADirection_Code+ '-' + macdcode + '-' + convergenceType
    return candleCode


def _lineNotify(payload, file=None):
    import requests

    url = "https://notify-api.line.me/api/notify"
    token = "EfFZH8Q3NZq6BUovs0TDHSCDCC8KMHSraCLSczapf6p"
    token= "mXNWLGiUzhOhsJw6f1sF1hGXNHeCDN3RhPksAHg977E"
    token = "nhEKEQa0ugEgqGolp580dMr2wxylcgJK4q63L7fL9pW"
    headers = {"Authorization": "Bearer " + token}
    return requests.post(url, headers=headers, data=payload, files=file)

def CreateFolder(folder_path) :
    
    # Specify the path of the folder
    # folder_path = 'path_to_your_folder'

    # Check if the folder exists
    if not os.path.exists(folder_path):
        # Create the folder
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    # else:
    #     print(f"Folder '{folder_path}' already exists.")

def writeTradeData(candleAnalysisArray,Desc_folder,thisTradeID,stDescAll)    :
    
    file_path =   Desc_folder + "/data_" + str(thisTradeID) + ".txt"
    # Write data to plain text file
    with open(file_path, 'w') as txt_file:
        for item in candleAnalysisArray:        
            if item['TradeID'] == thisTradeID :       
                txt_file.write(f"{item}\n") 
                  
    file_path =  Desc_folder + "/data_desc_" + str(thisTradeID) + ".txt"
    # Write data to plain text file
    with open(file_path, 'w') as txt_file:            
        txt_file.write(stDescAll)     
    
    return ''

def checkGraphStatus(I_want_money,curpair,startTimestmpCheck):
    
    
    return ''

def getActionByEMASlope(candleAnalysisArray,lastIndex):
    action = 'Idle'
    if candleAnalysisArray[lastIndex]['SlopeValue'] > candleAnalysisArray[lastIndex-1]['SlopeValue'] :
       SlopeDirection = 'Up' 
       action = 'CALL'
    else :
       SlopeDirection = 'Down'     
       action = 'PUT'
    
    return action 

def getActionByEMAAbove(candleAnalysisArray,lastIndex):
    action = 'Idle'
    if candleAnalysisArray[lastIndex]['EMA3'] > candleAnalysisArray[lastIndex]['EMA5'] :
       EMAAbove = '3' 
       action = 'CALL'
    else :
       EMAAbove = '5'     
       action = 'PUT'
    
    return action 

def UpdateTradeResult(candleAnalysisArray,tradeid,TradeStatus,buyno,profit,balance,currentAction,winStatus,MoneyTrade,Remark) :
    if profit > 0 :
       winStatus='Win' 
    if profit == 0 :
       winStatus='EQ'    
    if profit < 0 :
       winStatus='Loss'  
     
    lastIndex= len(candleAnalysisArray)-1
    candleAnalysisArray[lastIndex]['tradeid'] = tradeid
    candleAnalysisArray[lastIndex]['TradeStatus'] = TradeStatus
    
    candleAnalysisArray[lastIndex]['buyno'] = buyno
    candleAnalysisArray[lastIndex]['profit'] = profit 
    candleAnalysisArray[lastIndex]['profit'] = profit 
    candleAnalysisArray[lastIndex]['balance'] = balance
    candleAnalysisArray[lastIndex]['action'] = currentAction
    candleAnalysisArray[lastIndex]['WinStatus'] = winStatus
    candleAnalysisArray[lastIndex]['MoneyTrade'] = MoneyTrade
    candleAnalysisArray[lastIndex]['Remark'] = Remark
    
    # dataJsonString  = json.dumps(candleAnalysisArray)
    # json_obj = json.loads(dataJsonString)
    # url = 'https://lovetoshopmall.com/dataservice/saveTradeResult2.php' 
    # myobj = {
    # 'Mode':'SaveDetail99',
    # 'dataPost' : json_obj
    # }
    
    # x = requests.post(url, json = myobj)
    # print(x.text)
    # QMessageBox.about(self, 'Title',x.text)
    

    return candleAnalysisArray

def DefineBodyCode(Color,UpperHeightPercent,BodyHeightPercent,LowerHeightPercent)  :
    
    UCode = ''; LowerCode= '' ; BodyCode= ''
    if UpperHeightPercent > 0 and UpperHeightPercent < 10 : UCode = "U10"
    if UpperHeightPercent > 10 and UpperHeightPercent < 20 : UCode = "U20"
    if UpperHeightPercent > 20 and UpperHeightPercent < 30 : UCode = "U30"
    if UpperHeightPercent > 30 and UpperHeightPercent < 40 : UCode = "U40"
    if UpperHeightPercent > 40 and UpperHeightPercent < 50 : UCode = "U50"
    if UpperHeightPercent > 50 and UpperHeightPercent < 60 : UCode = "U60"
    if UpperHeightPercent > 60 and UpperHeightPercent < 70 : UCode = "U70"
    if UpperHeightPercent > 70 and UpperHeightPercent < 80 : UCode = "U80"
    if UpperHeightPercent > 80 and UpperHeightPercent < 90 : UCode = "U90"
    if UpperHeightPercent > 90  :  UCode = "U100"
    
    if LowerHeightPercent > 0  and   LowerHeightPercent < 10 : LowerCode = "L10"
    if LowerHeightPercent > 10 and   LowerHeightPercent < 20 : LowerCode = "L20"
    if LowerHeightPercent > 20 and   LowerHeightPercent < 30 : LowerCode = "L30"
    if LowerHeightPercent > 30 and   LowerHeightPercent < 40 : LowerCode = "L40"
    if LowerHeightPercent > 40 and   LowerHeightPercent < 50 : LowerCode = "L50"
    if LowerHeightPercent > 50 and   LowerHeightPercent < 60 : LowerCode = "L60"
    if LowerHeightPercent > 60 and   LowerHeightPercent < 70 : LowerCode = "L70"
    if LowerHeightPercent > 70 and   LowerHeightPercent < 80 : LowerCode = "L80"
    if LowerHeightPercent > 80 and   LowerHeightPercent < 90 : LowerCode = "L90"
    if LowerHeightPercent > 90  :   Lowee = "L100" 
    
    if BodyHeightPercent > 0  and   BodyHeightPercent < 10 : BodyCode = "B10"
    if LowerHeightPercent > 20 and  BodyHeightPercent < 30 : BodyCode = "B20"
    if BodyHeightPercent > 10 and   BodyHeightPercent < 20 : BodyCode = "B30"
    if BodyHeightPercent > 30 and   BodyHeightPercent < 40 : BodyCode = "B40"
    if BodyHeightPercent > 40 and   BodyHeightPercent < 50 : BodyCode = "B50"
    if BodyHeightPercent > 50 and   BodyHeightPercent < 60 : BodyCode = "B60"
    if BodyHeightPercent > 60 and   BodyHeightPercent < 70 : BodyCode = "B70"
    if BodyHeightPercent > 70 and   BodyHeightPercent < 80 : BodyCode = "B80"
    if BodyHeightPercent > 80 and   BodyHeightPercent < 90 : BodyCode = "B90"
    if BodyHeightPercent > 90  :   BodyCode= "B100" 
    
    
    return Color+ '-'+ UCode + '-' + BodyCode+ '-'+ LowerCode

def getEMA35_By_TALIB(candleList,curpair,DataMultiply,tradeid,tradestatus,buyno) :
    
    
    nArray = []
    for i in range(len(candleList)) :
        nArray.append(candleList[i]['close']) 
    
    
    close_prices = np.array(nArray)
    
    talib.set_compatibility(1)
    ema3 = talib.EMA(close_prices, timeperiod=3)
    ema5 = talib.EMA(close_prices, timeperiod=5) 
    
    ema3 = np.nan_to_num(ema3, nan=0)
    ema5 = np.nan_to_num(ema5, nan=0)
    i = 0
    numturnpoint = 0
    lastTurnPointID = 0
    
    # ถ้าดึงข้อมูล มาเป็น 100 หรือ 1000 ให้มาแก้เงื่อนไขในนี้
    DataMul = 1000*1000
    
    
    if buyno == 0 :        
        for item in candleList:
            
            item["curpair"] = curpair
            item["TradeStatus"] = tradestatus
            item["MinuteNo"] = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(item['from'])
            item["ema3"] = ema3[i] 
            item["ema5"] = ema5[i]
            item["tradeid"] = tradeid 
            item["differ"] = 0
            item["candleHeight"] = item['max']- item['min']
            
            item["buyno"] = 0
            item["profit"] = 0
            item["balance"] = 0
            item["action"] = ''
            item["WinStatus"] = ''
            item["CutPoint"] = ''
            item["MoneyTrade"] = 0
            
            
            item["TurnPoint"] = '??'             
            item["Remark"] = '' 
            item["actionLog"] = '' 
            
            
            
            if i >= 2 :
               candleList[i]["curpair"] = curpair 
               candleList[i]["TradeStatus"] = tradestatus
               item["actionLog"] = '' 
               if ema3[i-1] > ema3[i-2] and ema3[i-1] > ema3[i] :
                #   candleList[i-1]["TurnPoint"] = 'TurnToDown-' + str(candleList[i-1]["id"]  )
                  candleList[i-1]["TurnPoint"] = 'Turn2Down'
                  numturnpoint = numturnpoint+1
                  candleList[i-1]["turnpointno"] = numturnpoint                  
                  lastTurnPointID = candleList[i-1]["id"]
                  item["LastTurnPointID"] = lastTurnPointID
               if ema3[i-2] > ema3[i-1] and ema3[i-1] < ema3[i] :
                #   candleList[i-1]["TurnPoint"] = 'TurnToUp-'  + str(candleList[i-1]["id"] )
                  candleList[i-1]["TurnPoint"] = 'Turn2Up' 
                  numturnpoint = numturnpoint+1
                  candleList[i-1]["turnpointno"] = numturnpoint
                  lastTurnPointID = candleList[i-1]["id"]
                  
               
            item['turnpointno'] = numturnpoint  
            item["LastTurnPointID"] = lastTurnPointID
            candleList[i-1]["LastTurnPointID"] =  lastTurnPointID
            item["actionLog"] = '' 
            
            
            item["macd"] =  (ema3[i]- ema5[i] )* DataMultiply
            if item['ema3'] > item['ema5'] :
              item["emaAbove"] = '3'
            else :
              item["emaAbove"] = '5'  
                
            if item['close'] > item['open']:
                item['color'] = 'Green'
            if item['close'] < item['open']:
                item['color'] = 'Red'     
            if item['close'] == item['open']:
                item['color'] = 'Equal'  
                    
                
            if i > 0 : 
              item['SlopeValue'] = (ema3[i] - ema3[i-1] )* DataMultiply
            else :
              item['SlopeValue'] = 0.0
            
            if i > 0 : 
              if  item['SlopeValue'] < 0 :
                item['SlopeDirection'] =  'Down'  
              else :
                item['SlopeDirection'] =  'Up'
                
              
              item['emaConflict'] =''  
              item['convergence'] = '???'
              item["GreenCon"] = 0
              item["RedCon"] = 0
              item["actionLog"] = '' 
              
              if item['color'] =='Red' and item['emaAbove'] == '3':
                 item['emaConflict'] ='RED_ButEMA3Above'
              if item['color'] =='Green' and item['emaAbove'] == '5':
                 item['emaConflict'] ='GREEN_ButEMA5Above'   
              
              item['CandleHeight'] =  abs(item['max']-item['min'])  
              item['BodyHeight'] = (abs(item['close']-item['open']) )
              if item['close'] > item['open'] :
                 item['UpperHeight'] = (abs(item['max']-item['close']) )
                 item['LowerHeight'] = (abs(item['open']-item['min']) )
                 
              if item['close'] < item['open'] :
                 item['UpperHeight'] = (abs(item['max']-item['open']) )   
                 item['LowerHeight'] = (abs(item['close']-item['min']) )
                 
                 
              
              item['BodyHeightPercent'] = ((abs(item['close']-item['open']) )/ item['CandleHeight'] )*100 
              item['UpperHeightPercent'] = -1 ; item['LowerHeightPercent'] = -1 
              
              if item['color'] == 'Red' :
                 item['UpperHeightPercent']  = ((abs(item['max']-item['open']) )/ item['CandleHeight'] )*100 
                 item['LowerHeightPercent']  = ((abs(item['close']-item['min']) )/ item['CandleHeight'] )*100 
              if item['color'] == 'Green' :
                 item['UpperHeightPercent']  = ((abs(item['max']-item['close']) )/ item['CandleHeight'] )*100 
                 item['LowerHeightPercent']  = ((abs(item['open']-item['min']) )/ item['CandleHeight'] )*100  
                 
              if candleList[i-1]["emaAbove"] != candleList[i]["emaAbove"] :
                 candleList[i]["CutPoint"] = 'CUTTO_' + candleList[i]["emaAbove"]    
                  
            candleList[len(candleList)-1]['IdleLog'] = ''         
            i = i +1
    
    else :
        lastIndex= len(candleList)-1
        
        lastIndex2= len(candleList)-2
        lastIndex3= len(candleList)-3
        candleList[lastIndex]["GreenCon"] = 0 
        candleList[lastIndex]["RedCon"] = 0
        
        candleList[lastIndex]["actionLog"] = '' 
        
        # print('Last Index2=',lastIndex2)
        # print('Last Index3=',lastIndex3)
        candleList[lastIndex]["curpair"] = curpair 
        candleList[lastIndex]["MinuteNo"] = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[lastIndex]['from'])
        if candleList[lastIndex]["close"] > candleList[lastIndex]["open"] :
           candleList[lastIndex]["color"]  = 'Green'
           
        if candleList[lastIndex]["close"] < candleList[lastIndex]["open"] :
           candleList[lastIndex]["color"]  = 'Red'    
        
        if candleList[lastIndex]["close"] == candleList[lastIndex]["open"] :
           candleList[lastIndex]["color"]  = 'Equal'   
           
        if candleList[lastIndex]["color"] == candleList[lastIndex2]["color"]  :
           if candleList[lastIndex]["color"] == 'Green'  :
              candleList[lastIndex]["GreenCon"] = candleList[lastIndex2]["GreenCon"]+1
           else :
              candleList[lastIndex]["RedCon"] = candleList[lastIndex2]["RedCon"]+1     
        else :
           if candleList[lastIndex]["color"] == 'Green'  :
              candleList[lastIndex]["GreenCon"] = candleList[lastIndex2]["GreenCon"]+1
              candleList[lastIndex]["RedCon"] = 0 
           else :
              candleList[lastIndex]["RedCon"] = candleList[lastIndex2]["RedCon"]+1
              candleList[lastIndex]["GreenCon"] = 0     
            
        candleList[lastIndex]["ema3"] = ema3[len(ema3)-1]
        candleList[lastIndex]["ema5"] = ema5[len(ema5)-1]
        # candleList[lastIndex]["macd"] = (candleList[lastIndex]["ema3"] - candleList[lastIndex]["ema5"])*DataMultiply
        candleList[lastIndex]["macd"] = (ema3[len(ema3)-1] - ema5[len(ema3)-1])* DataMultiply
        if candleList[lastIndex]["ema3"] > candleList[lastIndex]["ema5"] :
           candleList[lastIndex]["emaAbove"] = '3'
        else :
           candleList[lastIndex]["emaAbove"] = '5'
           
        candleList[lastIndex]["SlopeValue"] = (candleList[lastIndex]["ema3"] - candleList[lastIndex2]["ema3"])* DataMultiply
        if candleList[lastIndex]["SlopeValue"]  < 0 :
           candleList[lastIndex]["SlopeDirection"]  = 'Down'
        else :
           candleList[lastIndex]["SlopeDirection"]  = 'Up' 
           
        candleList[lastIndex]["emaConflict"] = '**'   
        # print(candleList[lastIndex]["color"] ,' vs ',candleList[lastIndex]["emaAbove"] )
        if candleList[lastIndex]["color"]  == 'Red' and candleList[lastIndex]["emaAbove"]  == '3'   :
           candleList[lastIndex]["emaConflict"]  = 'CR' #'RedButAbove3' 
           
        if candleList[lastIndex]["color"]  == 'Green' and candleList[lastIndex]["emaAbove"]  == '5'   :
           candleList[lastIndex]["emaConflict"]  = 'CG'    
           
        candleList[lastIndex]["TurnPoint"] = '??'       
        if (candleList[lastIndex]["ema3"]  < candleList[lastIndex2]["ema3"] ) and  (candleList[lastIndex2]["ema3"]  > candleList[lastIndex3]["ema3"] ):
            candleList[lastIndex-1]["TurnPoint"] = 'Turn2Down'
            
        if (candleList[lastIndex3]["ema3"]  > candleList[lastIndex2]["ema3"] ) and  (candleList[lastIndex2]["ema3"]  < candleList[lastIndex]["ema3"] ):
            candleList[lastIndex-1]["TurnPoint"] = 'Turn2Up'    
           
        candleList[lastIndex]["CutPoint"] = ''           
        print(candleList[lastIndex]["emaAbove"]  ,' VS ' , candleList[lastIndex-1]["emaAbove"])
        if candleList[lastIndex]["emaAbove"]   !=  candleList[lastIndex-1]["emaAbove"]  :                      
           if candleList[lastIndex]["emaAbove"]  == '3'  and candleList[lastIndex-1]["emaAbove"]  == '5' :
              candleList[lastIndex]["CutPoint"]  = 'CutOccurTo_3'
           if candleList[lastIndex]["emaAbove"]  == '5'  and candleList[lastIndex-1]["emaAbove"]  == '3' :
              candleList[lastIndex]["CutPoint"]  = 'CutOccurTo_5'               
           print( '* ******** Cut Point Occur  = ',candleList[lastIndex]["CutPoint"]  ) 
        else :
           candleList[lastIndex]["CutPoint"] = ''                   
           A = 1 
            
        if abs(candleList[lastIndex]["macd"])  > abs(candleList[lastIndex2]["macd"] )  :
           candleList[lastIndex]["convergence"]  = 'Diver'
        else:
           candleList[lastIndex]["convergence"]  = 'Conver'    
           
        candleList[lastIndex]['UpperHeightPercent'] = 0   
        candleList[lastIndex]['LowerHeightPercent'] = 0   
        candleList[lastIndex]['BodyHeightPercent'] = 0   
        candleList[lastIndex]["CandleHeight"] =  abs(candleList[lastIndex]['max']- candleList[lastIndex]['min'])  
        candleList[lastIndex]["BodyHeight"] =  DataMul * abs(candleList[lastIndex]['close']- candleList[lastIndex]['open'])  
        
        if candleList[lastIndex]["close"] >  candleList[lastIndex]['open'] : 
           candleList[lastIndex]["UpperHeight"] =  DataMul * abs(candleList[lastIndex]['max']- candleList[lastIndex]['close'])      
           candleList[lastIndex]["LowerHeight"] =  DataMul * abs(candleList[lastIndex]['open']- candleList[lastIndex]['min'])
        
        if candleList[lastIndex]['close'] <  candleList[lastIndex]['open'] : 
           candleList[lastIndex]["UpperHeight"] =  DataMul * abs(candleList[lastIndex]['max']- candleList[lastIndex]['open'])      
           candleList[lastIndex]["LowerHeight"] =  DataMul * abs(candleList[lastIndex]['close']- candleList[lastIndex]['min'])
        
        
        candleList[lastIndex]["BodyHeightPercent"] =  ((abs(candleList[lastIndex]['close']-candleList[lastIndex]['open']) )/ candleList[lastIndex]['CandleHeight'] )*100 
        if candleList[lastIndex]['color'] == 'Red' :
            candleList[lastIndex]['UpperHeightPercent']  = ((abs(candleList[lastIndex]['max']-candleList[lastIndex]['open']) )/ candleList[lastIndex]['CandleHeight'] )*100 
            candleList[lastIndex]['LowerHeightPercent']  = ((abs(candleList[lastIndex]['close']-candleList[lastIndex]['min']) )/ candleList[lastIndex]['CandleHeight'] )*100 
        if candleList[lastIndex]['color'] == 'Green' :
            candleList[lastIndex]['UpperHeightPercent']  = ((abs(candleList[lastIndex]['max']-candleList[lastIndex]['close']) )/ candleList[lastIndex]['CandleHeight'] )*100 
            candleList[lastIndex]['LowerHeightPercent']  = ((abs(candleList[lastIndex]['open']-candleList[lastIndex]['min']) )/ candleList[lastIndex]['CandleHeight'] )*100     
        
        sCode  = DefineBodyCode(candleList[lastIndex]['color'],candleList[lastIndex]['UpperHeightPercent'],candleList[lastIndex]["BodyHeightPercent"],candleList[lastIndex]['LowerHeightPercent'])   
        print('-=Scode---------------' , sCode)
        candleList[lastIndex]['IdleLog'] = ''
        
        
           
        # if candleList[lastIndex]["emaAbove"]  == 5 and candleList[lastIndex2]["emaAbove"]  == 3   :
        #    candleList[lastIndex]["CutPoint"]  = 'Cut5Above'   
        
        
            
    # del candleList[0]
    # del candleList[1]
    # del candleList[2]
    # del candleList[3]
    # del candleList[4]
    # print('Step 2 = Len CandleList= ', len(candleList)) 
    # print('ID=', candleList[0]['id'] , '-' , candleList[len(candleList)-1]['id'])
    
    return ema3,ema5,candleList

def getActionByTurnPoint(candleAnalysisArray,lastIndex,actionArray,winArray,colorArray):
    
    action = 'Idle'
    isTurnPointOccur = False
    
    # Case A Turn Down จุด B จะเป็น Slope ลง (Red) เข้า Trade ตามจุด B
    if (candleAnalysisArray[lastIndex-2]['EMA3'] > candleAnalysisArray[lastIndex-1]['EMA3'] ) and (candleAnalysisArray[lastIndex-1]['EMA3'] < candleAnalysisArray[lastIndex]['EMA3'] ):
        isTurnPointOccur = True
        isTurnPointDirection = 'TurnUp' 
        action = 'CALL'
    
    # Case B Turn Up จุด B จะเป็น Slope ขึ้น (Green) เข้า Trade ตามจุด B
    if (candleAnalysisArray[lastIndex-2]['EMA3'] < candleAnalysisArray[lastIndex-1]['EMA3'] ) and (candleAnalysisArray[lastIndex-1]['EMA3'] > candleAnalysisArray[lastIndex]['EMA3'] ):
        isTurnPointOccur = True
        isTurnPointDirection = 'TurnDown'
        action = 'PUT'
    
           
    
    return action 

def getActionByEMACut(candleAnalysisArray):
    action = ''
    
    return action 


def AnalyBodyCandle(candleAnalysisArray) :
    
    if len(candleAnalysisArray) == 0 : return ''
    bodyHeight = 0  ; UHeight = 0  ; LHeight = 0 
    bodyHeightPercent = 0 ; UHeightPercent = 0 ;LHeightPercent = 0
    Multiply = 1000*1000
    lastIndex = len(candleAnalysisArray)-1  
    candleHeight = (candleAnalysisArray[lastIndex]['High'] - candleAnalysisArray[lastIndex]['Low'] )* Multiply
    if candleHeight == 0 : return bodyHeight,UHeight,LHeight,bodyHeightPercent,UHeightPercent,LHeightPercent
    if  candleAnalysisArray[lastIndex]['Open'] > candleAnalysisArray[lastIndex]['Close'] :
        color = 'Red'
        bodyHeight = (candleAnalysisArray[lastIndex]['Open']- candleAnalysisArray[lastIndex]['Close'])* Multiply
        UHeight = (candleAnalysisArray[lastIndex]['High']- candleAnalysisArray[lastIndex]['Open'])* Multiply
        LHeight = (candleAnalysisArray[lastIndex]['Close']- candleAnalysisArray[lastIndex]['Low'])* Multiply
        
        
    if  candleAnalysisArray[lastIndex]['Open'] < candleAnalysisArray[lastIndex]['Close'] :
        color = 'Green'   
        bodyHeight = (candleAnalysisArray[lastIndex]['Close']- candleAnalysisArray[lastIndex]['Open'] )* Multiply
        UHeight = (candleAnalysisArray[lastIndex]['High']- candleAnalysisArray[lastIndex]['Close'])* Multiply
        LHeight = (candleAnalysisArray[lastIndex]['Open']- candleAnalysisArray[lastIndex]['Low'])* Multiply
        
    if  candleAnalysisArray[lastIndex]['Open'] == candleAnalysisArray[lastIndex]['Close'] :
        color = 'Gray'    
        bodyHeight = (abs(candleAnalysisArray[lastIndex]['Open']- candleAnalysisArray[lastIndex]['Close']))* Multiply
        UHeight = (candleAnalysisArray[lastIndex]['High']- candleAnalysisArray[lastIndex]['Close'])* Multiply
        LHeight = (candleAnalysisArray[lastIndex]['Open']- candleAnalysisArray[lastIndex]['Low'])* Multiply
        
        
    bodyHeightPercent  =  round((bodyHeight/candleHeight)*100,4)
    print(bodyHeight,candleHeight,bodyHeight/candleHeight)
    UHeightPercent  =  round((UHeight/candleHeight)*100,4)
    LHeightPercent  =  round((LHeight/candleHeight)*100,4)
    
    
    
    
    return bodyHeight,UHeight,LHeight,bodyHeightPercent,UHeightPercent,LHeightPercent

def CreateAnalysisOFDataCandleArray(thisTradeID,candleAnalysisArray,StartTradeTime) :
    
    
    TurnPoint= ''
    lastIndex = len(candleAnalysisArray)-1  
    if (candleAnalysisArray[lastIndex]['EMA3']  < candleAnalysisArray[lastIndex-1]['EMA3'] ) and   candleAnalysisArray[lastIndex-1]['EMA3']  > candleAnalysisArray[lastIndex-2]['EMA3']  :
        candleAnalysisArray[lastIndex-1]['TurnPoint'] = 'TDown'
        print('T-Down Occur')
    
    if (candleAnalysisArray[lastIndex]['EMA3']  > candleAnalysisArray[lastIndex-1]['EMA3'] ) and   candleAnalysisArray[lastIndex-1]['EMA3']  < candleAnalysisArray[lastIndex-2]['EMA3']  :
        candleAnalysisArray[lastIndex-1]['TurnPoint'] = 'Up'    
        print('T-Up Occur')
    
    TurnPoint99 = candleAnalysisArray[lastIndex-1]['TurnPoint'] 
     
        
    file_path = "dataTrade/data_" + str(thisTradeID) + ".txt"
    # Write data to plain text file
    with open(file_path, 'w') as txt_file:
        for item in candleAnalysisArray:
           if item['TradeID'] == thisTradeID :
            txt_file.write(f"{item}\n")
            
    
    # QMessageBox.about(self, 'Title',x.text)        
    
    # print(candleAnalysisArray )
    return candleAnalysisArray,TurnPoint99

def getNewTradeID(curpair,targetmoney,BalanceOnIQ ) :
    
    # BalanceOnIQ  คือ ยอดเงิน ที่เชคจาก IQOption
    
    url = 'https://lovetoshopmall.com/dataservice/saveLabTrade2.php' 
    myobj = {
       'Mode' : 'getNewTradeNo' ,
       'curpair' : curpair ,
       'BalanceONIQ' : BalanceOnIQ,
       'targetmoney': targetmoney,
       'ThisTimeStamp': time.time()
      
    }
    # print(myobj)
    tradeResult = requests.post(url, json = myobj)    
    dataReturn = tradeResult.text 
    # print('Data = ',dataReturn)
    dataReturn2 = dataReturn.split('|')
    tradeid = dataReturn2[0]
    sectionno = dataReturn2[1]
    balanceOnMorning =  dataReturn2[2]
    
    
    return tradeid,sectionno,balanceOnMorning

def InitTrade(StartTradeTime,curpair,brokername,targetmoney,sectionname,candleAnalysisArray) :
    
    dataJsonString  = json.dumps(candleAnalysisArray)         
    json_obj = json.loads(dataJsonString)
    
    url = 'https://lovetoshopmall.com/dataservice/saveLabTrade2.php' 
    myobj = {
       'Mode' : 'InitTrade' ,
       'BrokerName' : brokername,
       'starttradetimestamp': StartTradeTime,    
       'curpair' : curpair,
       'targetMoney' : targetmoney ,
       'sectionname' : sectionname  ,
       'dataCandle' : json_obj 
    }
    # print(myobj)
    tradeResult = requests.post(url, json = myobj)    
    
    tradeResult = tradeResult.text 
    # print('รอบแรก ', tradeResult)
    tradeResult2 = tradeResult.split('#')
    tradeid = tradeResult2[0]
    sectionno = tradeResult2[1]
    # sectionname = tradeResult2[2]
    
    print('Trade ID = ' ,tradeid , ' section no = ',sectionno)
    
    
    return tradeid,sectionno,
    

def postDetailToCandlePureV2(Mode,sectionname,sectionno,buyno,tradeid,candleAnalysisArray) :
    
    
    dataJsonString  = json.dumps(candleAnalysisArray)         
    json_obj = json.loads(dataJsonString)
    url = 'https://lovetoshopmall.com/dataservice/saveLabTrade2.php' 
    # url = 'https://lovetoshopmall.com/test99.php' 
    
    myobj = {
       'Mode'  : Mode,
       'sectionname' : sectionname,
       'sectionno' :  sectionno,
       'buyno' : buyno,
       'tradeid': tradeid,          
       'dataPost' : json_obj
    }
    
    # print(myobj)
    x = requests.post(url, json = myobj)
    
    print('Post Detail To Candle Result = ' ,x.text)
    
    return ''
    
def FinishedTarget(tradeid,buyno ,balance,maxmoneytrade,stoptimestamp,sectionname,sectionno,candleAnalysisArray) :
    
    
    dataJsonString  = json.dumps(candleAnalysisArray)         
    json_obj = json.loads(dataJsonString)
    url = 'https://lovetoshopmall.com/dataservice/saveLabTrade2.php' 
    myobj = {
       'Mode'  : 'FinishedTarget',
       'sectionname':sectionname,
       'sectionno' : sectionno,
       'tradeid': tradeid,
       'numtrade' : buyno,
       'stoptimestamp': stoptimestamp,
       'maxmoneytrade' : maxmoneytrade,   
       'balance' : balance,
       'dataPost' : json_obj
    }
    
    # print(myobj)
    x = requests.post(url, json = myobj)
    
    print('Result = ' ,x.text)
    result  = x.text 
    result = result.split('#')
    
    balanceToday = result[0]
    countTradeToday = result[1]
    
    return balanceToday,countTradeToday
    
def FinishedTargetV2(tradeid,buyno ,balance,maxmoneytrade,stoptimestamp,sectionno,candleAnalysisArray) :
    
    
    dataJsonString  = json.dumps(candleAnalysisArray)         
    json_obj = json.loads(dataJsonString)
    url = 'https://lovetoshopmall.com/dataservice/saveLabTrade2.php' 
    myobj = {
       'Mode'  : 'FinishedTargetV2',       
       'sectionno' : sectionno,
       'tradeid': tradeid,
       'numtrade' : buyno,
       'stoptimestamp': stoptimestamp,
       'maxmoneytrade' : maxmoneytrade,   
       'balance' : balance,
       'dataPost' : json_obj
    }
    
    # print(myobj)
    x = requests.post(url, json = myobj)
    
    print('Result = ' ,x.text)
    result  = x.text 
    result = result.split('#')
    
    s1 = result[0]
    balanceToday = float(s1)
    countTradeToday = result[1]
    print('******************************  Result Post After Finished ********** ',x.text)
    
    return balanceToday,countTradeToday
            

def getActionByTurnPoint(candleAnalysisArray): 
    
    lastIndex = len(candleAnalysisArray) 
    # ตัวแปรที่บ่งบอกสภาวะของ แท่งเทียนมีดังนี้ 
    # 1.Color
    # 2.MACD จะเป็นตัวบอก Trend ว่า ขึ้นหรือลง ถ้า + ก็จะขึ้น ถ้า - ก็จะลง
    # 3.EMAAbove จะเป็นตัวบอก ว่าขณะนั้น EMA3 เหนือ EMA5 หรือ EMA5 เหนือ EMA3
    # 4.EMASlopeValue บ่งบอกค่าความชันของ EMA3 ถ้าน้อยกว่า 20 แสดงว่า EMA3 จะวิ่งแนวขนาน  
    # 5.EMAConvergence จะเป็นตัวบอกว่า กราฟมีการ ลู่เข้า หรือถ่างออก
    # 6.TurnPoint จะบอกว่า จุดที่ผ่านมา เป็น จุดกลับตัวหรือไม่ 
    # 7.CutPoint จะบอกว่า เกิดการตัดกันของ ema3 หรือ 5 หรือยัง 
    # 8.UHeight,BodyHeigh,LHeight จะเป็นตัวบอก ลักษณะแท่งเทียน 
    # 9.EMAConflict บ่งบอกว่า เกิดการขัดแย้งกันระหว่าง EMAAbove กับ Trend มักจะเกิดใน
    # กรณีที่ เส้น EMA ยังปรับตัวไม่ทันหลังจาก เกิดการกลับตัว เราเรียกว่า สภาวะ Conflict
    
    color = candleAnalysisArray[lastIndex]['color'] 
    macd = candleAnalysisArray[lastIndex]['macd'] 
    if macd < 0 :
       EMAAbove = 3 
    else :
       EMAAbove = 5
       
    EMASlopeValue = candleAnalysisArray[lastIndex]['ema3'] - candleAnalysisArray[lastIndex-1]['ema3']
    convergenceValue = abs(candleAnalysisArray[lastIndex]['macd']) -abs(candleAnalysisArray[lastIndex-1]['macd']) 
    
    
def getActionV3(candleAnalysis) :
    
    action = ''
    thislastIndex = len(candleAnalysis)-1
    macd = candleAnalysis[thislastIndex]['macd']
    emaSlope = candleAnalysis[thislastIndex]['SlopeValue']
    SlopeDirection = candleAnalysis[thislastIndex]['SlopeDirection']
    color  = candleAnalysis[thislastIndex]['color']
    stAction = ''
    print(' ที่ ActionV3 Slope Direction = ',SlopeDirection)
    
    # Layer ที่ 1 เลือกจาก Slope Direction
    # action = 'CALL' if SlopeDirection == 'UP' else 'PUT' 
    if SlopeDirection == 'Up' :
       action = 'CALL'
    else :
       action = 'PUT'      
       
    print('************ Step AAA: action = ' ,action)
    useCase =1 
    stAction = 'ใช้ Case-1'
    
    # Layer ที่ 2 เลือกจาก SlopeValue + macd
    if abs(macd) < 20 and abs(emaSlope) < 5 :
        #  มี 2 Case คือ Idle กับ Opposite
       action = 'Idle' 
       action = "CALL" if color == 'RED' else "PUT"
       if color == 'RED' :
          action = 'CALL'
       else  :
          action = "PUT"
       stAction = 'ใช้ Case-2'
       useCase =2
    
    print('get Action จาก getByV3 ', stAction , ' ได้ action =',action )
    
    return action,useCase 

def getFirstCandle(curpair) :

    
    I_want_money =IQ_Option('nutv99@gmail.com','Maithong11181')
    check, reason= I_want_money.connect()    #connect to iqoption
    if check == False:
       print('ไม่สามารถ Connect ได้ ' , reason ) 
       sys.exit(0)
    else : 
       if check:   
         numcandle = 5 ; Money = 1 ; action= 'PUT' ;expirations_mode = 1 ; buyno = 0  
         timeinterval = 60 ; dfMain = ''
         candleList,wincolor,TimeCandle,newservertimestamp  = getCandleByFirstRound(I_want_money, curpair,  numcandle) 
         
         if candleList[4]['open'] > candleList[4]['close'] :
            color = 'Red'
         else :
            color = 'Green'     
         print('เวลา ที่ firstCandle  function::', pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[4]['from']),' Color คือ ',color ) 
    
    return I_want_money,candleList

def getFirstCandleV2(I_want_money,curpair) :

    
    
    numcandle = 5 ; Money = 1 ; action= 'PUT' ;expirations_mode = 1 ; buyno = 0  
    timeinterval = 60 ; 
    candleList,wincolor,TimeCandle,newservertimestamp  = getCandleByFirstRound(I_want_money, curpair,  numcandle) 
              
    print('เวลา ที่ firstCandle  function::', pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[4]['from'])) 
    
    return candleList

def CreateAnalysisTmpFromClassList(tradeid,buyno,curpair,candleList,ema3,ema5,DataMultiply) :
    
    # ชื่อเก่า copyLastCandleListTo_candleAnalysis
    
    ema3 = ema3*DataMultiply
    ema5 = ema5*DataMultiply
    lastIndex = len(candleList) -1 
    if candleList[lastIndex]['open'] < candleList[lastIndex]['close'] : 
       color = 'Green'
    else :
       color = 'Red'    
       
    if ema3  > ema5 : 
       emaAbove = '3'
    else :
       emaAbove = '5'
    
    macd = (ema3-ema5 )
    if  abs(macd ) < 5  :    
        emaAbove = 'E'
       
    lastMinute =  pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[lastIndex]['from']) + ':00-'+pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[lastIndex]['to']) 
    candleHeight = abs(candleList[lastIndex]['max'] - candleList[lastIndex]['min']) * DataMultiply
    bodyHeight = abs(candleList[lastIndex]['close'] - candleList[lastIndex]['open']) * DataMultiply
    if color == 'Green' :
      UHeight = abs(candleList[lastIndex]['max'] - candleList[lastIndex]['close']) * DataMultiply
      LHeight = abs(candleList[lastIndex]['open'] - candleList[lastIndex]['min']) * DataMultiply
    else :
      UHeight = abs(candleList[lastIndex]['max'] - candleList[lastIndex]['open']) * DataMultiply
      LHeight = abs(candleList[lastIndex]['close'] - candleList[lastIndex]['min']) * DataMultiply  
        
    # if emaAbove == '3' and ema3
        
    # macd = (ema3 - ema5 ) * 1000*1000
       
       
    candleAnalysisTmp = {
    "TradeID"     : tradeid,
    "CandleATMinuteNo"  : lastMinute,  
    "CandleCode": '' ,
    "buyno" : buyno ,
    "useCase": '',
    "GenerateAction": "",
    "MinuteTrade": "",
    "EndMinuteTrade": "",
    "MoneyTrade": 0,    
    "WinStatus": "",
    "profit": 0.0,
    'balance':0.0,
    "curpair": curpair,
    "id":  candleList[lastIndex]['id'],
    "from": candleList[lastIndex]['from'],
    "to": candleList[lastIndex]['to'],
    "at":  candleList[lastIndex]['at'],
    "Open": candleList[lastIndex]['open'],
    "High": candleList[lastIndex]['max'],
    "Low": candleList[lastIndex]['min'],
    "Close": candleList[lastIndex]['close'],
    "Volume": candleList[lastIndex]['volume'],
    "color": color ,
    "LastMinute": lastMinute,
    "colorContinue": 0,
    
    "EMA3":ema3,
    "EMA5": ema5,
    "macd": macd ,
    "emaAbove" : emaAbove,
    "convergenceValue" :0.0,
    "convergenceType" :'',
    "SlopeValue": 0.0,
    "SlopeDirection": "",
    "signal_line":0 ,
    "histogram" : 0 ,    
    "EMA_Action" :'',
    "CandleHeight" : candleHeight ,
    "BodyHeight" : bodyHeight ,
    "UHeight" : UHeight ,
    "LHeight" : LHeight ,
    
    "isBreakPoint": "",
    "TurnPoint": "",
    "LastTurnPoint": 0,
    "isCutPoint": "",
    "LastCutPoint": 0,
    "isConflict": "",
    
    
  }
    
    
    return candleAnalysisTmp
    

def createScriptCreateTable():
    
    # Define the table name
    
    data_dict = {
    "id": 3253494,
    "from": 1706132400,
    "to": 1706132460,
    "at": 1706132460000000000,
    "Open": 1.013425,
    "High": 1.013425,
    "Low": 1.013205,
    "Close": 1.013285,
    "Volume": 0,
    "color": "R",
    "LastMinute": "04:40",
    "colorContinue": 0,
    "TurnPointType": "",
    "action": "PUT",
    "MoneyTrade": 1,
    "WinStatus": "Loss",
    "profit": -1,
    "SMA3": 1013301.6666666667,
    "SMA5": 1013292.9999999998,
    "EMA_short": 1013314.6874999999,
    "EMA_long": 1013335.0889092112,
    "macd": -20.40140921133471,
    "signal_line": -35.77063684426811,
    "histogram": 15.369227632933402,
    "SlopeValue": -29.687500000116415,
    "SlopeDirection": "Down",
    "EMAAbove": "5",
    "previous_EMAAbove": "5",
    "EMACut": "nan",
    "previous_SlopeDirection": "Up",
    "TurnPoint": "T-Down77"   }
   
    table_name = 'example_table' 
    create_table_script = f"CREATE TABLE {table_name} (\n" 
    
    for key, value in data_dict.items():
    # Infer data type based on the Python type of the sample value
       print('--->' , value,isinstance(value, str))
       if isinstance(value, str):
          data_type = 'VARCHAR(255)'
       elif isinstance(value, int):
          data_type = 'INT'
       
       create_table_script += f"    {key} {data_type},\n"   
    # Add more conditions for other data types as needed

    # Remove the trailing comma and add closing parenthesis
    create_table_script = create_table_script.rstrip(',\n') + "\n);"
    print(create_table_script)

    
    # sample_row = data_dict[list(data_dict.keys())[0]]
    # column_types = {key: type(sample_row[i]).__name__ for i, key in enumerate(data_dict.keys())}
  

    # for column_name, data_type in column_types.items():
    #   create_table_script += f"  {column_name} {data_type},\n"

    # create_table_script = create_table_script.rstrip(',\n') + "\n);"
   
    
    
def PostTradeToCandlePureV2Table(I_want_money,curpair,starttimestamp,lasttimestamp,totalminute) : 
    
    balance = 30 - totalminute 
    timeinterval = 60 
    LastCandleTimestamp = lasttimestamp + ((30-totalminute)*60)
    numcandle = 30 
    candleList = I_want_money.get_candles(curpair, timeinterval, numcandle, LastCandleTimestamp)
    df = getEMA3Dataframe(candleList)
    # print(df)
    
    return df

def getEMA3Dataframe(candleList):
    
    for i in range(0,len(candleList)) :
     candleList[i]["colorContinue"] = 0
     candleList[i]["SlopeValue"] = 0 
     candleList[i]["LastMinute"] = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[i]["from"] )
     candleList[i]["SlopeDirection"] = ''
     candleList[i]["TurnPointType"] = 'NoTurn'
     if candleList[i]["close"] > candleList[i]["open"] :
        candleList[i]["color"] = 'G'
     else :
       if candleList[i]["close"] < candleList[i]["open"] :
          candleList[i]["color"] = 'R'    
       else :         
          candleList[i]["color"] = 'E'     
     
    df = pd.DataFrame.from_dict(candleList)           
    df.rename(columns = {'open':'Open'}, inplace = True)
    df.rename(columns = {'close':'Close'}, inplace = True)
    df.rename(columns = {'min':'Low'}, inplace = True)
    df.rename(columns = {'max':'High'}, inplace = True)
    df.rename(columns = {'volume':'Volume'}, inplace = True)    
   #  df = pd.DataFrame(df, columns=['id','from','to','at', 'Open', 'High', 'Low', 'Close','Volume','color',
   #  'LastMinute' ,'colorContinue','SlopeValue','SlopeDirection','TurnPointType'])  
    df = pd.DataFrame(df, columns=['id','from','to','at', 'Open', 'High', 'Low', 'Close','Volume','color',
    'LastMinute' ,'colorContinue','TurnPointType','action','MoneyTrade','WinStatus','profit'])  
  
    a= 3  ; b= 5 ; c= 4
  
    EMA_short = df['Close'].ewm(span=a, adjust=False,min_periods= a+1).mean()
    EMA_long = df['Close'].ewm(span=b, adjust=False,min_periods= b+1).mean()
   
    SMA3  = df['Close'].rolling(3).mean()
    SMA5  = df['Close'].rolling(5).mean()
  
    MACD = EMA_short - EMA_long
    signal = MACD.ewm(span=c, adjust=False,min_periods=c+1).mean()
  
    df['SMA3'] = SMA3*1000*1000
    df['SMA5'] = SMA5*1000*1000
      
    df['EMA_short'] = EMA_short*1000*1000
    df['EMA_long'] = EMA_long*1000*1000
    
    df['EMA_short_pyt'] = EMA_short*1000*1000
    df['EMA_long_pyt'] = EMA_long*1000*1000
    
    df['macd'] = MACD*1000*1000
    df['macd_pyt'] = MACD*1000*1000
    
    
    df['signal_line'] = signal*1000*1000
    df['histogram'] = df['macd'] - df['signal_line'] 
    df['SlopeValue'] = df['EMA_short'] - df['EMA_short'].shift(1) 
    df['action'] = 'action'
    df['profit'] = 0.0
    df['TurnPointType'] = ''
    df['WinStatus'] = ''
    df['bodyHeight'] = abs(df['Close']-df['Open'])
    df['bodyHeightPoint'] = abs(df['Close']-df['Open']) 
    
    df['candleHeight'] = abs(df['High']-df['Low']) 
    
    
    
    
    df['LastMinute'] = ''
    df['action'] = ''
    
    
   #  print('Type = ',df.dtypes)
   #  print('dF SlopeValue',df['SlopeValue'])
    df.loc[(df['Close'] <  df['Open'] ), 'color'] = 'R' 
    df.loc[(df['Close'] >  df['Open'] ), 'color'] = 'G' 
    df.loc[(df['Close'] ==  df['Open'] ), 'color'] = 'E' 
   
    
    
    df.loc[(df['SlopeValue']< 0), 'SlopeDirection'] = 'Down' 
    df.loc[(df['SlopeValue']> 0), 'SlopeDirection'] = 'Up' 
    
    df.loc[(df['macd']< 0), 'EMAAbove'] = '5' 
    df.loc[(df['macd']> 0), 'EMAAbove'] = '3' 
    
    df['previous_EMAAbove'] = df['EMAAbove'].shift(1)
    df.loc[(df['previous_EMAAbove'] != df['EMAAbove'])  , 'EMACut'] = 'EMACutOccur' 
    
    
    df['previous_SlopeDirection'] = df['SlopeDirection'].shift(1)
    df.loc[(df['SlopeDirection'] != df['previous_SlopeDirection']) &  (df['SlopeDirection'] == 'Down' ), 'TurnPoint'] = 'T-Down77' 
    df.loc[(df['SlopeDirection'] != df['previous_SlopeDirection']) &  (df['SlopeDirection'] == 'Up' ), 'TurnPoint'] = 'T-Up99' 
    df.loc[(df['SlopeDirection'] == df['previous_SlopeDirection']) &  (df['SlopeDirection'] == 'Up' ), 'TurnPoint'] = 'UpCon' 
    df.loc[(df['SlopeDirection'] == df['previous_SlopeDirection']) &  (df['SlopeDirection'] == 'Down' ), 'TurnPoint'] = 'DownCon'  
    
    return df

def saveDFToCSV(df,csv_file_path,isMain):
    
    csv_file_path = 'datacandle.csv'
    # Write DataFrame to CSV file
    if isMain == True:
      last_row = df.iloc[-1]      
    else :
      last_row = df.iloc[-1]
      
      
    last_row_df = pd.DataFrame(last_row).transpose()    
    if isMain == True: 
      last_row_df.to_csv(csv_file_path,mode='w', header=True,index=False)
    else :
      last_row_df.to_csv(csv_file_path,mode='a', header=False,index=False)
      
      
def getEMA3(I_want_money,curpair,starttime):
    
    numcandle = 10 
    timeinterval = 60 
    data = I_want_money.get_candles(curpair, timeinterval, numcandle, starttime)
    close_prices = np.array([
    data[0]['close'],data[1]['close'],data[2]['close'],data[3]['close'],data[4]['close'],
    data[5]['close'],data[6]['close'],data[7]['close'],data[8]['close'],data[9]['close']        
    ])
    period = 3
    # candle 9 คือล่าสุด 0 คือ ย้อนหลังไป 9 นาที
    # เราต้องเปรียบเทียบ ema[9] กับ data[9]
    print(data[9]['from']-data[0]['from'])
    ema = talib.EMA(close_prices, timeperiod=period)
    if data[9]['close'] > data[9]['open'] :         
        differ = ema[9] - data[9]['close']         
        if ema[9] > data[9]['close'] :            
           action = 'PUT'
           print('Case Green-1 EMA อยู่สูงกว่า ระยะปิด = ' , differ) 
        else:
           action = 'CALL'
           print('Case Green2 EMA อยู่ต่ำกว่าระยะปิด Differ = ' , differ)  
    else :
         differ = ema[9] - data[9]['open']
         print('Case Red Differ EMA AND OPEN  = ' , differ) 
         if ema[9] > data[9]['open'] :
            action = 'PUT'
            print('Case Red-1 EMA อยู่สูงกว่า ระยะเปิด(Open) Differ = ' , differ) 
            
         if ema[9] < data[9]['close']  :
            action = 'CALL'
            print('Case Red-2 EMA อยู่ต่ำกว่า ระยะปิด(Close) Differ = ' , differ) 
            
         if ema[9] > data[9]['close'] and ema[9] < data[9]['open'] :
            print('Case Red-3 EMA วิ่งผ่านแท่ง ) Differ = ' , differ) 
            action = 'PUT'   
            
         if ema[9] > data[9]['open'] and ema[9] < data[9]['close'] :
            print('Case 44  Differ = ' , differ) 
            action = '  CALL'      
    
    return action
    
    
    

def getTimeRemain(I_want_money):
    
    expirations_mode = 1
    remaning_time=I_want_money.get_remaning(expirations_mode)
    # purchase_time=remaning_time-30
    return remaning_time 
    
     

def getNewCandle(I_want_money): 
    
    remain_time = getTimeRemain(I_want_money)
    if remain_time > 60 :
       print('เวลาเหลืออยู่ ', remain_time) 
    
def getActionByFollowTrend(candleAnalysisArray,lastIndex)    :
    
    # [{'curpair': 'EURUSD-OTC', 'id': 3257956, 'from': 1706400120, 'to': 1706400180,
    # 'at': 1706400121000000000, 'Open': 0.997615, 'High': 0.997615, 'Low': 0.997615, 
    # 'Close': 0.997615, 'Volume': 0, 'color': 'Red', 'LastMinute': '07:02', 
    # 'colorContinue': 0, 'EMA3': 0.9978641666666667, 'EMA5': 0.9977129999999998, 
    # 'macd': 151.16666666681323, 'SlopeValue': 0.0, 'SlopeDirection': '', 
    # 'TurnPoint': '', 'action': '',
    # 'MoneyTrade': 0, 'WinStatus': '', 'profit': 0.0, 'balance': 0.0}]
    action = 'CALL'
    TurnStatus= ''
    if candleAnalysisArray[lastIndex-1]['macd'] > 0 and candleAnalysisArray[lastIndex-1]['macd'] < 0 :
       candleAnalysisArray[lastIndex-1]['TurnPoint']    = 'TurnToDown' 
       TurnStatus  = 'TurnToDown' 
       
    if candleAnalysisArray[lastIndex-1]['macd'] < 0 and candleAnalysisArray[lastIndex-1]['macd'] > 0 :
       candleAnalysisArray[lastIndex-1]['TurnPoint']    = 'TunnToUp'
       TurnStatus  = 'TurnToUp' 
       
       
       
    return action 

def getiqservertimestamp(I_Want_Money):
    servertime = I_Want_Money.get_server_timestamp()
    return servertime


def getiqservertime(I_Want_Money):
    
    servertime = I_Want_Money.get_server_timestamp()
    print(servertime)
    dt_object = datetime.datetime.fromtimestamp(servertime)
    return dt_object

def getiqservertimeObject(I_Want_Money):
    import datetime  
    servertime = I_Want_Money.get_server_timestamp()
    dt_object = datetime.datetime.fromtimestamp(servertime)
    return dt_object


def LabCheckTradeProfit(I_Want_Money, curpair,numCandleTest):
    
    Profit = 0
    servertime = getiqservertimestamp(I_Want_Money) 
    serverdatetime = newutil.cv_TimeStamp_DateTime(servertime)
    timeinterval = 60*5
    numcandle = numCandleTest
    candleList = I_Want_Money.get_candles(curpair, timeinterval, numcandle, servertime)
    signalString = ""

    
    print('Lab Check Profit Test ',curpair , ' at ' , serverdatetime , ' Num Sample=',numcandle)
    signalarray = []
    for i in range(0, numcandle - 1):
        if candleList[i]["close"] > candleList[i]["open"]:
            signalString = signalString + "g-"
            signalarray.append('g')
        if candleList[i]["close"] < candleList[i]["open"]:
           signalString = signalString + "r-"
           signalarray.append('r')
        if candleList[i]["close"] == candleList[i]["open"]:
           signalString = signalString + "e-"
           signalarray.append('e')

    profitSt = '?-'
    balance = 0
    balanceSt = '0-'
    wincon = 0
    losscon = 0
    maxwincon = 2
    for i in range(1, len(signalarray) - 1):
        if (signalarray[i] == signalarray[i-1]) :
            profitSt = profitSt +  'w-'
            balance = balance + 0.85 
            balance = round(balance, 2)
            balanceSt  = balanceSt + '[' + str(balance) +']-'
            wincon = wincon +1 ; losscon = 0
        if (signalarray[i] != signalarray[i-1]) :
            profitSt = profitSt + 'l-'
            balance = balance - 1
            balance = round(balance, 2)
            balanceSt  = balanceSt + '[' +  str(balance) + ']'
            losscon = losscon +1 ; wincon = 0
            
    
    profitSt = profitSt + '?-'        
    print(signalString)
    print(profitSt)
    print(balanceSt)
    print(curpair ,'  Balance=',balance)
    
    return Profit


def checkAssetOpen(I_want_money, assetname):
    MODE = "PRACTICE"
    Money = 1
    ACTIVES = assetname
    ACTION = "put"
    expirations_mode = 1
    I_want_money.change_balance(MODE)
    if I_want_money.check_connect() == False:  # detect the websocket is close
        print("try reconnect")
        check, reason = I_want_money.connect()
        check, id = I_want_money.buy(Money, ACTIVES, ACTION, expirations_mode)
        if check:
            print("!buy!")
            return True
        else:
            print("buy fail")
            return False


def sma53(candleData):
    sma5 = 0
    sma3 = 0
    slope5 = 0
    slope3 = 0

    return sma5, sma3, slope5, slope3


def setModePractice(I_want_money):
    # MODE: "PRACTICE"/"REAL"
    MODE = "PRACTICE"
    I_want_money.change_balance(MODE)


def setModeReal(I_want_money):
    # MODE: "PRACTICE"/"REAL"
    MODE = "REAL"
    I_want_money.change_balance(MODE)


def getAPI(URL, CurrencyPair):
    jsonData = ""

    # location given here
    location = "delhi technological university"
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {"CurrencyPair": CurrencyPair}

    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=PARAMS)
    print(r)

    # extracting data in json format
    jsonData = r.json()

    return jsonData


def getMainAction():
    jsonData = ""
    CurrencyPair = ""
    PARAMS = {"CurrencyPair": CurrencyPair}
    URL = "https://lovetoshopmall.com/dataservice/getTradeAction3.php"
    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=PARAMS)
    # print("r is ",r)

    # extracting data in json format
    jsonData = r.json()

    return jsonData

def getCandleByFirstRound(I_want_money, curpair,  numcandle):
    
#  ดึง Data แท่งเทียนรอบแรก จะมีการปรับ เวลาให้ตรงก่อนดึง 
    
    servertimestamp = getiqservertimestamp(I_want_money)
    dtObj = getiqservertimeObject(I_want_money)
    print(dtObj.hour,':',dtObj.minute,':',dtObj.second)
    timeremain = getTimeRemain(I_want_money)
    
    '''
    แต่เดิม
    if timeremain > 60 : 
       timeremain  = timeremain - 60 
    print('เวลาเหลือ ',timeremain) 
    # timeremain ถ้ามากกว่า 60 หมายถึง ขณะนี้ มันอยู่ในรอบหรือช่วงเวลา รอผล ตัดสิน คือ วินาทีที่ 31-59
    time.sleep(timeremain)    
    '''
    # เปลี่ยนใหม่
    if timeremain > 60 : 
       timeremain  = timeremain - 60 
    if timeremain > 30 :
       print('เวลาเหลือ-2',30-timeremain ) 
       
    time.sleep(timeremain)
    timeinterval = 60 
    newservertimestamp = servertimestamp + timeremain 
    newservertimestamp = servertimestamp 
    # print('เวลาร้องขอ ครั้งแรก = ',  pdatetime.B22_cvTimestamp2TimeStr_NoSecond(newservertimestamp))
    # print('จำนวน Candle  = ', numcandle)
        
    candleList = I_want_money.get_candles(curpair, timeinterval, numcandle, newservertimestamp)
    data1 = candleList[numcandle-1]['from'] 
    print('Candle List เวลา :: ' , pdatetime.B22_cvTimestamp2TimeStr_NoSecond(data1) )
    wincolor = 'E'
    if candleList[numcandle-1]['close'] > candleList[numcandle-1]['open'] :
       wincolor = 'G' 
       print('สรุป Candle = Green ',curpair,'-',pdatetime.B2_cvTimestamp2DateStr(data1)) 
    else:
       wincolor = 'R'  
       print('สรุป Candle =  Red ',curpair,'-', pdatetime.B2_cvTimestamp2DateStr(data1)) 
       
    if candleList[numcandle-1]['close'] == candleList[numcandle-1]['open'] :    
        wincolor = 'E'  
        print('สรุป Candle =  Equal ',pdatetime.B2_cvTimestamp2DateStr(data1)) 
    
    # เวลาสิ้นสุด (ถึงเวลา)
    # print(pdatetime.B2_cvTimestamp2DateStr(data1))
    
    return candleList,wincolor,pdatetime.B2_cvTimestamp2DateStr(data1),newservertimestamp 

def getCandleByDateString(IQ, curpair, StartDatetimeString ,numcandle): 
    # ดึง Candle โดย กำหนด เวลาเริ่มต้น ถอยหลังไปเป็น จำนวน  numcandle
     
    # Format--->datetime_str = '09/19/22 13:55:26'    
    timeinterval = 60
    requestTimestamp = pdatetime.B6_dtstr_timestamp(StartDatetimeString)
    candleList = IQ.get_candles(curpair, timeinterval, numcandle, requestTimestamp)
    return candleList 

def getCandleByStartDateString(IQ, curpair, StartDatetimeString ,EndDatetimeString): 
    # ดึง Candle โดย กำหนด เวลาเริ่มต้น และ เวลาสิ้นสุด
    # StartDatetimeString = '9/19/22 13:55:26'    
    # EndDatetimeString  = '9/19/22 14:55:26'    
    thailand_timezone = pytz.timezone('Asia/Bangkok') 
    
    date_object1 = datetime.strptime(StartDatetimeString, "%m/%d/%y %H:%M:%S") 
    localized_time1 = thailand_timezone.localize(date_object1)
    print("Localized time in Thailand:", localized_time1)
    s1 = localized_time1.timestamp() 
    
    date_object2 = datetime.strptime(EndDatetimeString, "%m/%d/%y %H:%M:%S") 
    localized_time2 = thailand_timezone.localize(date_object2)
    print("Localized time2 in Thailand:", localized_time2)
    s2 = localized_time2.timestamp() 
    
    
    
    
    
    # date_object2 = datetime.strptime(EndDatetimeString, "%m/%d/%y %H:%M:%S") 
    # s2 = date_object2.timestamp()
    timeinterval = 60
    
    NumDifferMinute  = (s2 - s1)/60 
    numcandle = int(NumDifferMinute)
    print(s1,'-',s2, '=',numcandle) 
    candleList = IQ.get_candles(curpair, timeinterval, numcandle, s2)
    Time1 = candleList[0]['from'] - 420
    print('First Time Candle = ', pdatetime.B22_cvTimestamp2TimeStr_NoSecond(Time1))
    
    return candleList     


def getCandleByIntervalDateString(IQ, curpair, StartDatetimeString ,EndDatetimeString): 
    # ดึง Candle โดย กำหนด เวลาเริ่มต้น และ เวลาสิ้นสุด
    # StartDatetimeString = '9/19/22 13:55:26'    
    # EndDatetimeString  = '9/19/22 14:55:26'    
     
    date_object1 = datetime.strptime(StartDatetimeString, "%m/%d/%y %H:%M:%S") 
    s1 = date_object1.timestamp()
    
    date_object2 = datetime.strptime(EndDatetimeString, "%m/%d/%y %H:%M:%S") 
    s2 = date_object2.timestamp()
    timeinterval = 60
    
    NumDifferMinute  = (s2 - s1)/60 
    numcandle = int(NumDifferMinute)
    # print(s1,'-',s2, '=',numcandle) 
    candleList = IQ.get_candles(curpair, timeinterval, numcandle, s2)
    
    return candleList     


def getPureCandle3(IQ, curpair, timeinterval, starttime,TotalCandle,convertToDataFrame):
    
    allCandle = []
    balance = TotalCandle
    end_from_time = starttime
    print('End From Time Step1 ',pdatetime.B2_cvTimestamp2DateStr(end_from_time))
    while balance > 0 :
       if balance > 1000 : 
          thisnumcandle = 1000
          balance = balance - 1000
       else :
          thisnumcandle = balance  
          balance = 0    
          
       candleList = IQ.get_candles(curpair, timeinterval, thisnumcandle, end_from_time)
       allCandle = candleList + allCandle 
       end_from_time = int(candleList[0]["from"])-1
       print('End From Time Step 2 ',pdatetime.B2_cvTimestamp2DateStr(end_from_time))
       
       
    if convertToDataFrame == True: 
        df = pd.DataFrame.from_dict(allCandle)                
        df.rename(columns = {'open':'Open'}, inplace = True)
        df.rename(columns = {'close':'Close'}, inplace = True)
        df.rename(columns = {'min':'Low'}, inplace = True)
        df.rename(columns = {'max':'High'}, inplace = True)
        df.rename(columns = {'volume':'Volume'}, inplace = True)    
        df = pd.DataFrame(df, columns=['id','from','to','at', 'Open', 'High', 'Low', 'Close','Volume'])  
        return df 
    else :    
        return allCandle 
       
    
def CandleToDataFrame(candleData):
    
    df = pd.DataFrame.from_dict(candleData)           
    df.rename(columns = {'open':'Open'}, inplace = True)
    df.rename(columns = {'close':'Close'}, inplace = True)
    df.rename(columns = {'min':'Low'}, inplace = True)
    df.rename(columns = {'max':'High'}, inplace = True)
    df.rename(columns = {'volume':'Volume'}, inplace = True)    
    df = pd.DataFrame(df, columns=['id','from','to','at', 'Open', 'High', 'Low', 'Close','Volume'])  
        
    return df 
    
def calEMA(df,shortPeriod,LongPeriod,Signal) :
    
    a= shortPeriod  ; b= LongPeriod ; c= Signal
    # a=3 ; b=5 ; c= 4
    EMA_short = df['Close'].ewm(span=a, adjust=False,min_periods= a+1).mean()
    EMA_long = df['Close'].ewm(span=b, adjust=False,min_periods= b+1).mean()
    
    SMA3  = df['Close'].rolling(3).mean()
    SMA5  = df['Close'].rolling(5).mean()
    
    MACD = EMA_short - EMA_long
    signal = MACD.ewm(span=c, adjust=False,min_periods=c+1).mean()
    df['SMA3'] = SMA3
    df['SMA5'] = SMA5
    
    df['EMA_short'] = EMA_short*1000*1000
    df['EMA_long'] = EMA_long*1000*1000
    df['macd'] = MACD*1000*1000
    df['signal_line'] = signal*1000*1000
    df['histogram'] = df['macd'] - df['signal_line']  
    
    turnPoint  = ['','','','','','']
    EMA3Slope  = ['','','','','','','']
    
    datePoint = [] 
    color = [] 
    conver = ['','','','','','','']
    TurnPoint  = ['','','','','','','']
    
    for i in range(0,len(df)) :
        candleTimne = pdatetime.B2_cvTimestamp2TimeStr(df['from'][i]) 
        datePoint.append(candleTimne)
        if df['Close'][i] > df['Open'][i] :
           color.append('G')
        else :
           color.append('R')
    
    for i in range(6,9) :        
        if df['macd'][i-1] > df['macd'][i] :
            conver.append('Conver')
        else :
            conver.append('Diver')
            
        if df['EMA_short'][i-1] > df['EMA_short'][i] :
            EMA3Slope.append('Down')
        else :
            EMA3Slope.append('Up')
        
        if (df['EMA_short'][i-1] > df['EMA_short'][i]) and  (df['EMA_short'][i-1] > df['EMA_short'][i-2] ) :
            TurnPoint.append('TurnToDown')
        else :
           if (df['EMA_short'][i-1] < df['EMA_short'][i]) and  (df['EMA_short'][i-1] < df['EMA_short'][i-2] ) :
              TurnPoint.append('TurnToUp')  
           else :
              TurnPoint.append('--')  
         
     
    df['fromTime'] = datePoint
    df['color'] = color
    df['EMA3Slope'] = EMA3Slope
    df['TurnPoint'] = TurnPoint
    df['conver'] = conver
    
    return df
       
    

def getCandle(IQ, curpair, numcandle,timeserver):
    
    # candleList = IQ.get_candles(curpair, timeinterval, numcandle, timeserver)
    candleList = IQ.get_candles(curpair, 60, numcandle, timeserver)

    # print(type(candleList))
    # print(len(candleList))
    # totalList= len(candleList)

    # # print(candleList[totalList-1]['close'])
    # maxPrice = candleList[totalList-1]['max']
    # minPrice = candleList[totalList-1]['min']
    # open =  candleList[totalList-1]['open']
    # close =  candleList[totalList-1]['close']
    # totalHeight = maxPrice - minPrice
    # getShape(maxPrice,minPrice,open,close)
    return candleList


def getCandle2(IQ, curpair, timeinterval, numcandle, startTime):
    candleList = IQ.get_candles(curpair, timeinterval, numcandle, startTime)

    # print(type(candleList))
    # print(len(candleList))
    # totalList= len(candleList)

    # # print(candleList[totalList-1]['close'])
    # maxPrice = candleList[totalList-1]['max']
    # minPrice = candleList[totalList-1]['min']
    # open =  candleList[totalList-1]['open']
    # close =  candleList[totalList-1]['close']
    # totalHeight = maxPrice - minPrice
    # getShape(maxPrice,minPrice,open,close)
    return candleList


def getCandleASDataFrame(IQ, curpair, timeinterval, numcandle):
    candleList = IQ.get_candles(curpair, timeinterval, numcandle, time.time())
    df = pd.DataFrame(
        candleList,
        columns=["id", "from", "at", "to", "open", "close", "min", "max", "volume"],
    )

    return df,candleList


def SaveCandlePostToTable(url, currenyPair, data):
    # url = 'https://lovetoshopmall.com/dataservice/saveCandle.php'
    tradeTime = time.time()
    expirations_mode = 60

    myobj = {
        "Mode": "savecandle",
        "currencyPair": currenyPair,
        "tradetime": tradeTime,
        "intervalSecTime": expirations_mode,
        "dataCandle": data,
    }

    x = requests.post(url, json=myobj)
    print("Post Result is ", x.text)

    return 1


def SaveTradeLab(data, i, curpair, MoneyTrade, Profit, tradetype, winstatus, seriesno):
    url = "https://lovetoshopmall.com/dataservice/saveTradeResult2.php"
    tradeTime = time.time()
    expirations_mode = 60

    myobj = {
        "Mode": "savelabcandle",
        "seriesno": seriesno,
        "currencyPair": curpair,
        "dataCandle": data[i],
        "tradeno": i,
        "tradeType": tradetype,
        "MoneyTrade": MoneyTrade,
        "Profit": Profit,
        "winstatus": winstatus,
    }

    x = requests.post(url, json=myobj)

    # print("Post Result is ", x.text)

    return 1


def SaveTradeLabV2(
    data, i, curpair, MoneyTrade, Profit, balance, tradetype, winstatus, seriesno
):
    url = "https://lovetoshopmall.com/dataservice/saveTradeResult3.php"
    tradeTime = time.time()
    expirations_mode = 60

    myobj = {
        "Mode": "savelabcandle",
        "seriesno": seriesno,
        "currencyPair": curpair,
        "dataCandle": data[i],
        "tradeno": i,
        "tradeType": tradetype,
        "MoneyTrade": MoneyTrade,
        "Profit": Profit,
        "Balance": balance,
        "winstatus": winstatus,
    }

    x = requests.post(url, json=myobj)

    # print('Post Result is ',x.text)

    return 1


def SaveTradeLabV3(
    i,
    curpair,
    MoneyTrade,
    Profit,
    balance,
    tradetype,
    winstatus,
    seriesno,
    timetrade,
    tradeResult,
):
    url = "https://lovetoshopmall.com/dataservice/saveTradeResult3_2.php"
    tradeTime = time.time()
    expirations_mode = 60

    myobj = {
        "Mode": "savelabcandle",
        "seriesno": seriesno,
        "currencyPair": curpair,
        "tradeno": i,
        "BuyWithAction": tradetype,
        "tradeResult": tradeResult,
        "MoneyTrade": MoneyTrade,
        "Profit": Profit,
        "Balance": balance,
        "winstatus": winstatus,
        "timetrade": timetrade,
    }

    x = requests.post(url, json=myobj)

    print("Post Result is ", x.text)

    return 1


def checkInsideBar(data):
    for i in range(5, len(data) - 10):
        if data[i]["max"] > data[i + 1]["max"]:
            print((i, data[i]["close"]))

    return 1


def checkOutsideBar(data):
    for i in range(5, len(data) - 10):
        if data[i]["max"] > data[i + 1]["max"]:
            print((i, data[i]["close"]))

    return 1


def getTradeByContinueWin(I_Want_Money, curpair, numcandle, startCandleTime, seriesno):
    strategies = ""

    signal = []
    timefrom = []
    print("Start get Candle at", startCandleTime)
    data = getCandle2(I_Want_Money, curpair, 60, numcandle, startCandleTime)
    print("Total Data =", len(data))

    for i in range(0, numcandle - 1):
        if data[i]["close"] > data[i]["open"]:
            signal.append("g")
            timefrom.append(data[i]["from"])
        else:
            signal.append("r")
            timefrom.append(data[i]["from"])

    print("Total Signal=", len(signal))
    wincon = 0
    losscon = 0
    lastresult = ""

    greencon = 0
    redcon = 0
    maxgreencon = []
    maxredcon = []

    for i in range(0, len(signal)):
        if i == 0:
            lastsignal = signal[i]
        else:
            if lastsignal == signal[i]:
                if signal[i] == "r":
                    redcon = redcon + 1
                else:
                    greencon = greencon + 1
            else:
                lastsignal = signal[i]
                if signal[i] == "r":
                    redcon = 1
                    maxgreencon.append(greencon)
                else:
                    greencon = 1
                    maxredcon.append(redcon)

    print("MaxRedCon", maxredcon)
    print("MaxGreenCon", maxgreencon)
    # lastsignal2 = [signal[numcandle-5],signal[numcandle-4],signal[numcandle-3],signal[numcandle-2],signal[numcandle-1]]
    # print('lastsignal -->',lastsignal2)
    dangerSignal = "n"

    # if signal[numcandle-4] =='r' and signal[numcandle-3]=='g' and signal[numcandle-2] =='r' and signal[numcandle-1]=='g':
    #     dangerSignal ='y'
    # if signal[numcandle-4] =='g' and signal[numcandle-3]=='r' and signal[numcandle-2] =='g' and signal[numcandle-1]=='r':
    #     dangerSignal ='y'

    print(curpair, " Danger Signal is", dangerSignal)
    fromtime = datetime.datetime.fromtimestamp(timefrom[0])
    # endtime = datetime.datetime.fromtimestamp(timefrom[numcandle-1])
    endtime = ""

    balance = LabByCandle(curpair, data, timefrom, numcandle, seriesno)
    print(curpair + " Balance is", balance, " at time ", fromtime, "-", endtime)

     
    return balance


def getShape(maxPrice, minPrice, open, close):
    shape = "N"
    if open < close:
        Upper = maxPrice - close
        bodyHeight = close - open
        Trend = "U"
    else:
        Upper = maxPrice - close
        bodyHeight = open - close
        Trend = "D"

    if open == close:
        bodyHeight = 0
        Trend = "E"

    sectionHeight = (maxPrice - minPrice) / 10
    if Trend == "u":
        if open <= sectionHeight * 2:
            shape = "shootingstar"
        if close - open <= sectionHeight:
            shape = "doji"

    return shape


def saveClassListToTxtFile(data, sFileName):
    # f = open(sFileName, "w")
    # print(data)
    df = pd.DataFrame(data)
    df.to_csv(sFileName)


def loginIQ():
    
    error_password = """{"code":"invalid_credentials","message":"You entered the wrong credentials. Please check that the login/password is correct."}"""
    I_want_money = IQ_Option("nutv99@gmail.com", "Maithong11181")
    # print(I_want_money.check_connect())

    check, id = I_want_money.connect()  # connect to iqoption
    if check:
        print("Login Success ID= ",id)
    else:
        print("Login Fail")
        pygame.init()
        # my_sound = pygame.mixer.Sound('applause.wav')
        my_soundError = pygame.mixer.Sound('mixkit-dog-barking-twice-1.wav')
        my_soundError.play()
        sys.exit(0)

    return I_want_money

def loginIQWithPass(username,password):
    
    error_password = """{"code":"invalid_credentials","message":"You entered the wrong credentials. Please check that the login/password is correct."}"""
    I_want_money = IQ_Option(username,password)
    # print(I_want_money.check_connect())

    check, id = I_want_money.connect()  # connect to iqoption
    if check:
        print("Login Success ID= ",id)
        LoginSuccess = True
    else:
        
        LoginSuccess = False
        
        

    return I_want_money,LoginSuccess


def LabByCandle(curpair, data, timefrom, numcandle, seriesno):
    profit = 0
    url = ""
    startaction = data[0]["close"]
    winstring = ''
    candleColor = []
    for i in range(0, len(data) - 1):
        if data[i]["close"] > data[i]["open"]:
            candleColor.append("g")
        else:
            candleColor.append("r")

    print("In LabByCandle len Of Signal=", len(candleColor))

    thisaction = candleColor[0]
    thismoney = 1
    balance = 0
    for i in range(1, len(candleColor)):
        if thisaction == candleColor[i]:
            win = "y"
            winstring = winstring +'y-'
            if thismoney <= 8:
                thismoney = thismoney * 2
        else:
            win = "n"
            winstring = winstring +'n-'
            thismoney = 2

        if win == "y":
            profit = 0.85 * thismoney
        else:
            profit = -thismoney

        # print(timefrom[i])
        dt_object = datetime.datetime.fromtimestamp(timefrom[i])
        dt_objectTime = dt_object.time()

        balance = balance + profit
        differ = data[i]["close"] - data[i]["open"]
        if data[i]["close"] - data[i]["open"] > 0:
            print(
                "Close > Open ", data[i]["close"], "-", data[i]["open"], " = ", differ
            )
        else:
            print("Close < Open ", data[i]["close"], "-", data[i]["open"], differ)

        print(
            i,
            ") ", timefrom[i], '-',
            dt_objectTime,
            " MoneyTrade= ",
            thismoney,
            "  ",
            thisaction,
            " vs ",
            candleColor[i],
            "-->",
            profit,
            " Balance = ",
            balance,
        )
        thisaction = candleColor[i]
        # SaveCandlePostToTable(url,curpair,data)
        SaveTradeLab(data, i, curpair, thismoney, profit, thisaction, win, seriesno)
        # msg = msg  + str(i) +' ) ' + dt_objectTime
        # msg = msg + constrtime(str(i),dt_objectTime) + ' '+ thisaction,' vs '
        # + candleColor[i] + '-->' +"\n"
        msg = ""
        print(winstring)
        print(msg)
        # + (profit) + ' Balance = '+ balance +")"  +"\n"

    msg = ""
    f = open("labtrade.txt", "a")
    f.write(msg)
    f.close()

    return balance


def constrtime(strTxt, time_object):
    time_string = time_object.strftime("%H:%M:%S")  # Format as HH:MM:SS
    message = strTxt + time_string

    return message


def SaveSummarize(currenyPair, startTradeTime, endTradeTime, Balance):
    url = "https://lovetoshopmall.com/dataservice/savesummarizefromLab.php"
    tradeTime = time.time()
    expirations_mode = 60

    myobj = {
        "Mode": "savesummarizefromLab",
        "currencyPair": currenyPair,
        "startTradetime": startTradeTime,
        "endTradetime": endTradeTime,
        "intervalSecTime": expirations_mode,
        "Balance": Balance,
    }

    x = requests.post(url, json=myobj)
    print("Post Result is ", x.text)

    return 1


def cvtimestamp(datestring):
    element = datetime.datetime.strptime(datestring, "%d-%m-%Y")
    timestamp = datetime.datetime.timestamp(element)

    return timestamp


def saveRealTrade(
    tradeTime, action, moneytrade, winstatus, resultColor, profit, balance
):
    url = "https://lovetoshopmall.com/dataservice/saveRealTrade.php"
    myobj = {
        "tradetime": tradeTime,
        "action": action,
        "resultColor": resultColor,
        "winstatus": winstatus,
        "profit": profit,
        "balance": balance,
    }
    x = requests.post(url, json=myobj)
    # data = json.loads(data)
    # # Write JSON string to a text file
    # with open(sFileName, 'w') as file:
    #    file.write(data)

    # f.close()


def getTechnical(Iq, curpair):
    asset = "GBPUSD"
    indicators = Iq.get_technical_indicators(curpair)
    print(indicators)


def cvTimestampToDateTime(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)

    return dt_object


def cvTimestampToDateTimeString(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    dt_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    return dt_str


def dateExample():
    timestamp = 1545730073
    # convert the timestamp to a datetime object in the local timezone
    dt_object = datetime.fromtimestamp(timestamp)
    # print the datetime object and its type
    print("dt_object =", dt_object)  # -->2018-12-25 09:27:53

    # convert from datetime to timestamp
    ts = datetime.timestamp(dt_object)

    # แปลง String->Date Object อ้างอิง https://pynative.com/python-datetime-format-strftime/
    # import---> from datetime import datetime
    start_time = "2:13:57"
    end_time = "11:46:38"
    # convert time string to datetime oject
    t1 = datetime.strptime(start_time, "%H:%M:%S")
    t2 = datetime.strptime(end_time, "%H:%M:%S")
    print("Start time:", t1.time())
    print("End time:", t2.time())

    #   Calculate Time Difference ระหว่าง  Datetime Object 2 อัน
    delta_second = t2 - t1
    # time difference in seconds
    #    print(f"Time difference is {delta_second.total_seconds()} seconds")
    min = delta_second / 60
    #    print('difference in minutes:', min)
    hours = delta_second / (60 * 60)
    #    print('difference in hours:', hours)

    # คำนวณผลต่าง เวลาระหว่าง 2 Timestamp
    start_ts = 1652426243.907874
    end_ts = 1652436243.907874
    # convert timestamps to datetime object
    dt1 = datetime.fromtimestamp(start_ts)
    print("Datetime Start:", dt1)
    dt2 = datetime.fromtimestamp(end_ts)
    print("Datetime End:", dt2)

    # Difference between two timestamps
    # in hours:minutes:seconds format
    delta = dt2 - dt1
    print("Difference is:", delta)  # -->2:46:40
    print("Difference is seconds:", delta.total_seconds())  # --> 10000.0

def LoginIQ():
    
    email = 'nutv99@gmail.com'
    password ='Maithong11181'
    I_want_money=IQ_Option(email,password)
    loginchecked,id = I_want_money.connect()#connect to iqoption
    
    if loginchecked == True:
        print('Login Success')
    else :
        print('Login Fail')
        exit(0)
        
    return I_want_money,loginchecked,id

def CheckWin(I_want_money,id) :
    
    profit =  I_want_money.check_win_v3(id)
    
    return profit

def ConvertData2DataFrame999(data)     :
      
        df = pd.DataFrame.from_dict(data)        
        df.rename(columns = {'open':'Open'}, inplace = True)
        df.rename(columns = {'close':'Close'}, inplace = True)
        df.rename(columns = {'min':'Low'}, inplace = True)
        df.rename(columns = {'max':'High'}, inplace = True)
        df.rename(columns = {'volume':'Volume'}, inplace = True)
    
        df = pd.DataFrame(df, columns=['id','from','to','at', 'Open', 'High', 'Low', 'Close','Volume'])
        
        a=12 ; b=21 ; c= 9
        a=3 ; b=5 ; c= 4
        EMA_short = df['Close'].ewm(span=a, adjust=False,min_periods= a+1).mean()
        EMA_long = df['Close'].ewm(span=b, adjust=False,min_periods= b+1).mean()
        MACD = EMA_short - EMA_long
        signal = MACD.ewm(span=c, adjust=False,min_periods=c+1).mean()
        df['EMA_short'] = EMA_short
        df['EMA_long'] = EMA_long
        df['macd'] = MACD
        df['signal_line'] = signal
        df['histogram'] = df['macd'] - df['signal_line'] 
        
        df['shift_hist'] = df['histogram'].shift(1)
        df[(df['histogram'] > 0) & (df['shift_hist'] < 0)]
        df.loc[(df['histogram']> 0) &  (df['shift_hist'] < 0 ), 'action'] = 'buy'
        df.loc[(df['histogram']< 0) &  (df['shift_hist'] > 0 ), 'action'] = 'sell' 
        
        diff = df['Open'] - df['Close']
        diff_pct = diff / df['Open']
        df.loc[df['action'] == 'buy', 'marker_position'] = df['Low']  
        df.loc[df['action'] == 'sell', 'marker_position'] = df['High'] 
        
        
        df['SMA3'] = df['Close'].rolling(3).mean()
        df['SMA5'] = df['Close'].rolling(5).mean()
        # print(df['action'])
        
        return df


def classList2JSON(classlistdata):
    
    data_json_string = json.dumps(classlistdata) # ได้ String 
    data_json  = json.loads(data_json_string)        
    return data_json

def classList2String(classlistdata):
    
    data_json_string = json.dumps(classlistdata) # ได้ String 
    
    return data_json_string

def String2JSON(dataString):    
    data_json  = json.loads(dataString)        
    return data_json

def JSON2String(dataJSON):    
    
    data_string  = json.dumps(dataJSON)        
    return data_string

def ClassList2DF(classList):
    
    import pandas as pd
    
    df = pd.DataFrame.from_dict(classList)
    return df

    
def csv2DF(filename)    :
    
    df = pd.read_csv(filename)
    print(df['from'][0])
    # print(df.to_string()) 
    
def AnalyzeCandleData(data)    :
    
    action ='put'
    return action

def getCandleByInterval(I_want_money ,curpair,startDate,endDate)     :
    
    
    timeinterval = 60
    # startDate= '12/10/23 00:00:00'
    # endDate= '12/10/23 13:00:00'
    
    startTimestamp = pdatetime.B23_cvDateString2Timestamp(startDate)
    endTimestamp = pdatetime.B23_cvDateString2Timestamp(endDate)
    diffTimeStamp = endTimestamp - startTimestamp 
    # print('ผลต่าง Timestamp = ' , diffTimeStamp)
    totalCandle = int(diffTimeStamp /60) +1 
    print('ต้องการ Total Candle=',totalCandle)
    # print('Start Time Stamp =',startTimestamp)
    ListData = []
    while totalCandle  > 0 :
          data = I_want_money.get_candles(curpair, timeinterval, totalCandle, endTimestamp)
          ListData.append(data)
          endTimestamp = data[0]['from']
          totalCandle = totalCandle - len(data)
          
    
    FirstCandle=  pdatetime.B2_cvTimestamp2DateStr(data[0]['from'])
    print('First Candle =', FirstCandle )
    #   print(data[0]['from'])
    # LastCandle=  pdatetime.B2_cvTimestamp2DateStr(data[totalCandle-1]['from'])
    # print('First Candle =', FirstCandle, ' Last Candle = ', LastCandle)

    

    return data

def checkHistoryTrade(I_want_money,numcandle) :
    
    # ประวัติการเข้า Trade จาก IQOption
    historyList= I_want_money.get_optioninfo(numcandle) 
    print(historyList)


def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Set a timeout in seconds

    try:
        sock.connect((host, port))
        print(f"Port {port} on {host} is open")
    except (socket.timeout, socket.error):
        print(f"Port {port} on {host} is closed")
    finally:
        sock.close() 

def getActionByEMASlopeOnly(datacandle,lastIndex):
    
    # หา action จาก ทิศทางของ ema3 ว่าขึ้นหรือลง โดยไม่ดู ขนาดหรือความชันของ ema3
    
    EMA3SlopeValue = datacandle[lastIndex]['EMA3'] -  datacandle[lastIndex-1]['EMA3'] 
    if EMA3SlopeValue > 0 : 
       EMA3Direction = 'Up' 
       currentAction = 'CALL'
    else : 
      EMA3Direction = 'Down'
      currentAction = 'PUT' 
    
    
    return EMA3Direction,currentAction 

def getEMA_ByTALib(candleList,period):
    # close_prices = np.array([candleList[0]['close'], candleList]['close'], candleList[2]['close'],candleList[3]['close'],    candleList[4]['close'],candleList[5]['close'],candleList[6]['close'],candleList[7]['close'], candleList[8]['close'],candleList[9]['close'] )
    
    nArray = []
    for i in range(len(candleList)) :
        nArray.append(candleList[i]['close']) 
    
    # close_prices = np.append(nArray)
    close_prices = np.array(nArray)
    
    
    
    talib.set_compatibility(1)
    emaList = talib.EMA(close_prices, timeperiod=period)
    
    return emaList
    
# ลักษณะ sma5 ต่างๆ
# Case แท่งแดง

#  1.สูงกว่า Max และสูงกว่า open-->A
#  2.อยู่ระหว่าง Max กับ open-->A2
#  3.ปาดหัวคือ อยู่ระหว่าง open กับ 80% ของ Body -->A3
#  4.อยู่ต่ำกว่า  50% ของ Body แต่มากกว่า close -->A4
#  5 อยู่
# เอาง่ายๆ ก่อน คือ พิจารณา อยู่เหนือหรือใต้ max,min เป็นพอ

def copyCandleList2CandleAnaly(curpair,candleList,candleAnalysis,ema3,ema5):
  
#   print('Step- 1 len =',len(candleList))
  buyno = 0
  for i in range (5,len(candleList)) :
#   for i in range(1,len(candleAnalysis)) :    
    
    buyno = buyno+1
    DataMultiply = 1000*1000
    lastIndex = len(candleList)-1
    lastIndex = i 
    lastIndexEMA = len(ema3)-1
    
    candleAtMinuteNo = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[lastIndex]['from'])+ ' TO '  +pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleList[lastIndex]['to'])
    macd = ema3[lastIndex] - ema5[lastIndex]
    if macd > 0 :
        emaAbove = '3' 
    else:
        emaAbove = '5'    
    
    UHeight = 0
    LHeight = 0
    
    if candleList[lastIndex]['open'] > candleList[lastIndex]['close'] :
        #   Red
        UHeight = (candleList[lastIndex]['max']- candleList[lastIndex]['open'])*DataMultiply   
        LHeight = (candleList[lastIndex]['close']- candleList[lastIndex]['min'])*DataMultiply   
        
    if candleList[lastIndex]['open'] < candleList[lastIndex]['close'] :
        #   Green
        UHeight = (candleList[lastIndex]['max']- candleList[lastIndex]['close'])*DataMultiply   
        LHeight = (candleList[lastIndex]['open']- candleList[lastIndex]['min'])*DataMultiply   
        
    candleHeight = abs(candleList[lastIndex]['max']- candleList[lastIndex]['min']  ) * DataMultiply
    
    candleAnalysisTmp = {
        "TradeID"     : 0,
        "CandleATMinuteNo"  : candleAtMinuteNo,  
        "CandleCode": '' ,
        "buyno" : 0 ,
        "useCase": '',
        "GenerateAction": "",
        "MinuteTrade": "",
        "EndMinuteTrade": "",
        "MoneyTrade": 0,    
        "WinStatus": "",
        "profit": 0.0,
        'balance':0.0,
        "curpair": curpair,
        "id":  candleList[lastIndex]['id'],
        "from": candleList[lastIndex]['from'],
        "to": candleList[lastIndex]['to'],
        "at":  candleList[lastIndex]['at'],
        "Open": candleList[lastIndex]['open'],
        "High": candleList[lastIndex]['max'],
        "Low": candleList[lastIndex]['min'],
        "Close": candleList[lastIndex]['close'],
        "Volume": candleList[lastIndex]['volume'],
        "color": '' ,
        "LastMinute": '',
        "colorContinue": 0,
        
        "EMA3":ema3[lastIndex],
        "EMA5": ema5[lastIndex],
        "macd": macd ,
        "emaAbove" : emaAbove,
        "convergenceValue" :0.0,
        "convergenceType" :'',
        "SlopeValue": 0.0,
        "SlopeDirection": "",        
        "EMA_Action" :'',
        "CandleHeight" : candleHeight ,
        "BodyHeight" : (abs(candleList[lastIndex]['open'] - candleList[lastIndex]['close']))* DataMultiply ,
        "UHeight" : UHeight*DataMultiply,
        "LHeight" : LHeight*DataMultiply ,
        "Trend" :"-" ,
        "isBreakPoint": "",
        "TurnPoint": "NoTurnPoint",
        "LastTurnPoint": 0,
        "isCutPoint": "",
        "LastCutPoint": 0,
        "isConflict": "",
        
    } 
    candleAnalysis.append(candleAnalysisTmp)
    del candleAnalysisTmp
    
   
#   print(len(candleAnalysis))
  
#  End Add 
  lastTurnPoint = 0 
  for i in range(len(candleAnalysis)) :
    # print('i=', i, ' = ',candleAnalysis[i]['EMA3'] , candleAnalysis[i-1]['EMA3']   )
      candleAnalysis[i]['SlopeValue'] = candleAnalysis[i]['EMA3'] - candleAnalysis[i-1]['EMA3']   
      
      
      
      
    #   candleAnalysis[i]['CandleATMinuteNo'] = pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleAnalysis[i]['from']) + ' ถึง ' + pdatetime.B22_cvTimestamp2TimeStr_NoSecond(candleAnalysis[i-1]['to'] )  
      
      if candleAnalysis[i]['Close'] >  candleAnalysis[i]['Open'] :
         candleAnalysis[i]['color'] = 'Green'
      if candleAnalysis[i]['Close'] <  candleAnalysis[i]['Open'] :
         candleAnalysis[i]['color'] = 'Red'
      if candleAnalysis[i]['Close'] ==  candleAnalysis[i]['Open'] :   
         candleAnalysis[i]['color'] = 'EQ'
     
      if abs(candleAnalysis[i]['macd']) >  abs(candleAnalysis[i-1]['macd']) :   
         candleAnalysis[i]['convergenceType'] = 'Diver' 
      else :
         candleAnalysis[i]['convergenceType'] = 'Conver'  
         
      if candleAnalysis[i-1]['macd'] < 0  and  candleAnalysis[i]['macd'] > 0 :   
         candleAnalysis[i]['isCutPoint'] = 'EMA-CutPoint' 
      
      if candleAnalysis[i-1]['macd'] > 0  and  candleAnalysis[i]['macd'] < 0 :   
         candleAnalysis[i]['isCutPoint'] = 'EMA-CutPoint' 
      
         
      if candleAnalysis[i]['SlopeValue'] > 0 :
         candleAnalysis[i]['SlopeDirection'] = 'UP'
         if candleAnalysis[i]['SlopeDirection'] == 'UP' :
            thisTrend = 'Up1' 
            if candleAnalysis[i]['emaAbove'] == '3' :
               thisTrend = 'Up2' 
               if candleAnalysis[i]['color'] == 'G' :
                  thisTrend = 'Up3'  
      else:
         candleAnalysis[i]['SlopeDirection'] = 'Down'
         thisTrend = 'Down1' 
         if candleAnalysis[i]['SlopeDirection'] == 'Down' :
            thisTrend = 'Down-1' 
            if candleAnalysis[i]['emaAbove'] == '5' :
               thisTrend = 'Down-2' 
               if candleAnalysis[i]['color'] == 'R' :
                  thisTrend = 'Down-3'  
      
      if abs(candleAnalysis[i]['SlopeValue']) < 15 and  abs(candleAnalysis[i]['macd']) > 15  : 
         thisTrend = 'SideWay1'  
      
      if abs(candleAnalysis[i]['SlopeValue']*1000*1000) < 15 and  abs(candleAnalysis[i]['macd']*1000*1000) < 15 : 
         thisTrend = 'SideWay2'     
          
          
      candleAnalysis[i]['Trend'] = thisTrend 
      
      
      if candleAnalysis[i]['SlopeDirection'] ==  'Up' and  candleAnalysis[i]['emaAbove'] ==  '5' :   
         candleAnalysis[i]['isConflict'] = 'conflict-5'
         
      if candleAnalysis[i]['SlopeDirection'] ==  'Down' and  candleAnalysis[i]['emaAbove'] ==  '3' :   
         candleAnalysis[i]['isConflict'] = 'conflict-3' 
         
      if i >= 2  :
         if (candleAnalysis[i-1]['EMA3'] > candleAnalysis[i-2]['EMA3']) and (candleAnalysis[i-1]['EMA3'] > candleAnalysis[i]['EMA3']) :
            candleAnalysis[i]['TurnPoint'] = 'Turn2Down'
            lastTurnPoint =  buyno-1 
            # print('Turn To Down Occur')
             
         if (candleAnalysis[i-1]['EMA3'] < candleAnalysis[i-2]['EMA3']) and (candleAnalysis[i-1]['EMA3'] < candleAnalysis[i]['EMA3']) :
            candleAnalysis[i]['TurnPoint'] = 'Turn2UP'
            lastTurnPoint = buyno-1 
            # print('Turn To Up Occur')
           
      candleAnalysis[i]['LastTurnPoint']  = lastTurnPoint 
    #   print('i=', i, ' = ',candleAnalysis[i]['CandleATMinuteNo'],' ; ', candleAnalysis[i]['SlopeValue'] , ' = ',candleAnalysis[i]['SlopeDirection'], ' = ',candleAnalysis[i]['color'] , ' EMA Above= '+ candleAnalysis[i]['emaAbove'] , ' CONVER=' + candleAnalysis[i]['convergenceType'])
  
  return candleAnalysis


def getCandleAnalysisArray(I_want_money,curpair,buyno,CandleRawDataArray,CandleAnalysisArray,servertime) :
    
    if buyno == 1 :
       numcandle = 10 
       candleList,wincolor,firstTime,servertime  = getCandleByFirstRound(I_want_money, curpair,  numcandle)
       CandleRawDataArray = candleList
       
    else :
       numcandle = 1 ; timeinterval = 60 
       candleList =  I_want_money.get_candles(curpair, timeinterval, numcandle, servertime)
       del CandleRawDataArray[0]
       CandleRawDataArray.append(candleList)
       print(CandleRawDataArray)
    
    lastIndex = len(CandleRawDataArray)-1
    # LastTime =  pdatetime.B22_cvTimestamp2TimeStr_NoSecond (CandleRawDataArray[lastIndex]['from'])
    LastTime =  CandleRawDataArray[lastIndex]['from']
    print('AT Buyno', buyno,' Len Of RawData=',len(CandleRawDataArray),' Last Time=', LastTime)   
    ema3,ema5 =  getEMA35_By_TALIB(candleList)
    # ema3,ema5 =  getEMA35_By_TALIB(CandleRawDataArray)
    
    
    candleAnalysisArray = copyCandleList2CandleAnaly(curpair,candleList,CandleAnalysisArray,ema3,ema5) 
    # leAnaly(curpair,candleList,CandleAnalysisArray,ema3,ema5) 
    # leAnaly(curpair,candleList,CandleAnalysisArray,ema3,ema5) 
    
    
    return CandleRawDataArray,candleAnalysisArray,servertime
    
    # candleList = getFirstCandleV2(I_want_money,curpair) 

def decimal_to_binary_array(decimal_number):
    # แปลงตัวเลขฐานสิบเป็นเลขฐานสอง
    binary_string = bin(decimal_number)[2:]  # [2:] เพื่อเอา '0b' ที่ขึ้นต้นออกไป
    # แปลงสตริงเป็นอาร์เรย์ของสตริง
    binary_array = list(binary_string)
    return binary_array

def filter_consecutive_duplicates(binary_array):
    # กรองข้อมูลให้เหลือแค่อาร์เรย์ที่มี 2 สมาชิกติดกันเหมือนกัน
    result = []
    for i in range(len(binary_array) - 1):
        if binary_array[i] == binary_array[i + 1]:
            result.append(binary_array[i] * 2)  # เพิ่มสมาชิกซ้ำกันในรูปแบบ '00' หรือ '11'
    return result

    