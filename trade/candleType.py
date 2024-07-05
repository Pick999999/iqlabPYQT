import talib as ta
from talib.abstract import *


import pandas as pd



# สร้างฟังก์ชันสำหรับตรวจสอบประเภทของแท่งเทียน
def classify_candlestick(row : dict):
    
    if row['close'] > row['open']:
        body_top = row['close']
        body_bottom = row['open']
    else:
        body_top = row['open']
        body_bottom = row['close']
    
    if row['high'] == body_top and row['low'] == body_bottom:
        return 'Marubozu'
    elif row['high'] == body_top and row['low'] < body_bottom:
        return 'Hammer'
    elif row['high'] > body_top and row['low'] == body_bottom:
        return 'Shooting Star'
    elif row['high'] == body_top and row['low'] > body_bottom:
        return 'Hanging Man'
    elif row['open'] == row['close']:
        return 'Doji'
    else:
        return 'Other'

# ใช้ apply เพื่อสร้างคอลัมน์ใหม่เพื่อบ่งบอกประเภทของแท่งเทียน
# df['candlestick_type'] = df.apply(classify_candlestick, axis=1)

# แสดงผลลัพธ์
# print(df)
