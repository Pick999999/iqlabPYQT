# การใช้ indicator ในการตรวจสอบว่าตลาดอยู่ในสถานะ Sideways Trend (แนวโน้มแบบข้างๆ) อาจมีหลายวิธี ซึ่งบาง indicator อาจช่วยในการตรวจสอบสถานะนี้ได้ดังนี้:

# Bollinger Bands (BB): เมื่อราคาอยู่ในช่วงแนวราบ พื้นที่ระหว่างเส้นบนและเส้นล่างของ Bollinger Bands จะมีความกว้างเพิ่มขึ้น ส่งผลให้ช่วงราคามีความผันผวนน้อย
# Average True Range (ATR): การลดลงของค่า ATR อาจแสดงถึงการเคลื่อนไหวของราคาที่มีความผันผวนน้อยลง และอาจช่วยในการตรวจสอบ Sideways Trend
# Moving Average (MA): เมื่อราคาอยู่ในช่วงแนวราบ ราคามักจะไล่เข้ามาใกล้เส้น MA โดย MA จะเป็นแนวทางของราคาในช่วงเวลาที่กำหนด
# Volume Profile: การใช้ Volume Profile สามารถช่วยในการตรวจสอบการซื้อขายในช่วงราคาที่แน่นอน ซึ่งอาจช่วยในการระบุ Sideways Trend
# Relative Strength Index (RSI): RSI ที่อยู่ในช่วงค่ามากกว่า 70 หรือน้อยกว่า 30 อาจช่วยในการระบุช่วง Sideways Trend โดย RSI ที่อยู่ในช่วง 30-70 อาจแสดงถึงการแนวโน้มที่ข้ามขึ้น-ลงอยู่
import sys

import mylib
import pdatetime 
# sys.path.append('../mybot')
import pandas as pd
import time 
import json
from iqoptionapi.stable_api import IQ_Option     


import time

import numpy as np 
import csv
import pygame
# from pygame import mixer  # Load the popular external library
import requests
import talib as ta
from talib.abstract import *
import talib 


def MYIndicator():
    print('indicatorTALIB')

def createStochastic(candleList) :
    
    # ตัวอย่างรายการราคา
    high = pd.Series([50.0, 52.0, 48.0, 45.0, 47.0, 49.0, 46.0, 50.0, 52.0, 55.0])
    low = pd.Series([45.0, 48.0, 42.0, 40.0, 42.0, 45.0, 42.0, 45.0, 48.0, 50.0])
    close = pd.Series([47.0, 50.0, 45.0, 42.0, 45.0, 48.0, 44.0, 47.0, 50.0, 53.0])

    # คำนวณ Stochastic Oscillator
    slowk, slowd = talib.STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

    print("SlowK:", slowk)
    print("SlowD:", slowd)

def createRSI(candleList) :
    
    # Calculate RSI
    close_pricesList0 = [candlestick["close"] for candlestick in candleList]
    # nArray = []
    # for i in range(len(candleList)) :
    #     nArray.append(candleList[i]['close']) 
    
    
    close_pricesList = np.array(close_pricesList0)
    rsi = talib.RSI(close_pricesList, timeperiod=14)

    return rsi

def createATR(candleList) :
    
    open_pricesList0 = [candlestick["open"] for candlestick in candleList]
    close_pricesList0 = [candlestick["close"] for candlestick in candleList]
    
    high_pricesList0 = [candlestick["max"] for candlestick in candleList]
    low_pricesList0 = [candlestick["min"] for candlestick in candleList]
    
    close_pricesList = np.array(close_pricesList0)
    open_pricesList = np.array(open_pricesList0)
    high_pricesList = np.array(high_pricesList0)
    low_pricesList = np.array(low_pricesList0)
    
    
    # Calculate ATR
    atr = talib.ATR(high_pricesList, low_pricesList, close_pricesList, timeperiod=14)
    
    return atr 

def createBB(candleList) :
    
    close_pricesList0 = [candlestick["close"] for candlestick in candleList]
    # nArray = []
    # for i in range(len(candleList)) :
    #     nArray.append(candleList[i]['close']) 
    
    
    close_pricesList = np.array(close_pricesList0)
    # Calculate Bollinger Bands
    upper_band, middle_band, lower_band = talib.BBANDS(close_pricesList, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    
    return upper_band, middle_band, lower_band


def CreateMACDV2(candleList,indexno: int ,fastperiod : int, slowperiod :int, signalperiod:int ) :


    # close_pricesList0 = [candlestick["RawData"]["close"] for candlestick in candleList]
    close_pricesList0 = []
    for i in range(indexno,len(candleList)) :
        close_pricesList0.append(candleList[i]['RawData']['close']) 
    
    
    close_pricesList = np.array(close_pricesList0)
    
    talib.set_compatibility(1)
    # Calculate MACD
    macd, signal, hist = talib.MACD(close_pricesList, fastperiod, slowperiod, signalperiod)
    ema3 = talib.EMA(close_pricesList, timeperiod=3)
    ema5 = talib.EMA(close_pricesList, timeperiod=5) 
    
    ema3 = np.nan_to_num(ema3, nan=0)
    ema5 = np.nan_to_num(ema5, nan=0) 
    macd = np.nan_to_num(macd, nan=0) 
    signal = np.nan_to_num(signal, nan=0) 
    
    return ema3,ema5,macd,signal,hist
    
    

def CreateMACD(candleList,fastperiod : int, slowperiod :int, signalperiod:int ) :


    close_pricesList0 = [candlestick["close"] for candlestick in candleList]
    # nArray = []
    # for i in range(len(candleList)) :
    #     nArray.append(candleList[i]['close']) 
    
    
    close_pricesList = np.array(close_pricesList0)
    
    talib.set_compatibility(1)
    # Calculate MACD
    macd, signal, hist = talib.MACD(close_pricesList, fastperiod, slowperiod, signalperiod)
    ema3 = talib.EMA(close_pricesList, timeperiod=3)
    ema5 = talib.EMA(close_pricesList, timeperiod=5) 
    
    ema3 = np.nan_to_num(ema3, nan=0)
    ema5 = np.nan_to_num(ema5, nan=0) 
    rsi = createRSI(candleList) 
    atr = createATR(candleList)
    
    upper_band, middle_band, lower_band = createBB(candleList)
    
    # print(ema3)
    print(type(ema3))
    json_data = json.dumps(candleList, indent=4)
    data_dict = json.loads(json_data) 
    
    i = 0
    for data_dict2 in data_dict:
        data_dict2['emaShort'] = ema3[i]
        data_dict2['emaLong'] = ema5[i]
        data_dict2['macd'] = macd[i]
        data_dict2['signal'] = signal[i]
        data_dict2['hist'] = hist[i]                
        data_dict2['rsi'] = rsi[i]                
        data_dict2['atr'] = atr[i]                
        
        data_dict2['upper_band'] = upper_band[i]                
        data_dict2['lower_band'] = lower_band[i]                
        data_dict2['middle_band'] = middle_band[i]                
        
        
        i = i +1
    
    
    
    

    n = len(data_dict)-5
    
    
    # print(data_dict[n]['emaLong']-data_dict[n]['emaShort'] , ' macd ' , data_dict[n]['macd'] )
    # print (data_dict)
    
    
    # dict_of_dicts = {idx: d for idx, d in enumerate(candleList)}
    # print(dict_of_dicts)
    # dict_of_dicts['ema333'].append(ema3)
    # print(dict_of_dicts)
    
    # data_dict_list = [obj.to_dict() for obj in candleList]
    # print(data_dict_list)
    
    # print(len(candleList),' vs ', len(ema3))
    # candleList['ema333'].extend(ema3)
    # print(candleList)

    
    # append to dataframe
    # df = pd.DataFrame(candleList)
    # df['emaShort'] = ema3
    # print(df)

def createStocastic(candleList) :
    
    highList = [] ; lowList = [] ; closeList = [] 
    for i in range(0,9) :
        highList.append(candleList[i]['max'])
        lowList.append(candleList[i]['min'])
        closeList.append(candleList[i]['close'])
        
    
    # ตัวอย่างรายการราคา
    # high = pd.Series([50.0, 52.0, 48.0, 45.0, 47.0, 49.0, 46.0, 50.0, 52.0, 55.0])
    # low = pd.Series([45.0, 48.0, 42.0, 40.0, 42.0, 45.0, 42.0, 45.0, 48.0, 50.0])
    # close = pd.Series([47.0, 50.0, 45.0, 42.0, 45.0, 48.0, 44.0, 47.0, 50.0, 53.0])
    high = pd.Series(highList) ; low = pd.Series(lowList) ; close = pd.Series(closeList) 
    

    # คำนวณ Stochastic Oscillator
    slowk, slowd = talib.STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

    print("SlowK:", slowk)
    print("SlowD:", slowd)
    
    
    
    
    
