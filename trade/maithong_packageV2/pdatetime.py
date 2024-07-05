import sys
import time
# import datetime
from datetime import datetime


def A1_getCurrentTimeStamp():
    # ได้ timestamp
   return time.time()
   
      
def A2_getCurrentObjectDateTime():        
    # ได้ dateObject
    return datetime.fromtimestamp(time.time())   

def A3_getCurrentDateTimeStr():        
    
    # ได้ dateString
    dt_object = datetime.fromtimestamp(time.time())   
    print(dt_object)
    datetimeStr = dt_object.strftime("%d/%m/%Y, %H:%M:%S")
    return datetimeStr
    
    
    
def B1_cvTimestamp2Object(timestampvalue):
    
    # รับค่า  timestamp->datetimeObject
    return datetime.fromtimestamp(timestampvalue)   

def B2_cvTimestamp2DateStr(timestampvalue):    
    # รับค่า  timestamp->datetimestr
    dt_object = datetime.fromtimestamp(timestampvalue)   
    datetimeStr = dt_object.strftime("%d/%m/%Y, %H:%M:%S")
    return datetimeStr

def B9_getDayOfWeekFromTimestamp(timestampvalue):
        
    # dt = datetime.utcfromtimestamp(timestampvalue)
    dt = datetime.fromtimestamp(timestampvalue)

    # Get the day name in full format (e.g., Monday, Tuesday)
    day_name = dt.strftime('%A')
    # Get the day of the week as an integer (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
    # day_of_week = dt.weekday()
    # # Define a list of day names
    # days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # # Get the day name using the day_of_week integer
    # day_name = days[day_of_week]
    
    return day_name

def B2_cvTimestamp2TimeStr(timestampvalue):    
    # รับค่า  timestamp->datetimestr
    dt_object = datetime.fromtimestamp(timestampvalue)   
    datetimeStr = dt_object.strftime("%H:%M:%S")
    return datetimeStr

def B22_cvTimestamp2TimeStr_NoSecond(timestampvalue):    
    # รับค่า  timestamp->datetimestr
    dt_object = datetime.fromtimestamp(timestampvalue)   
    datetimeStr = dt_object.strftime("%H:%M")
    return datetimeStr



def B3_cvDateObj2TimeStamp(dateObj):    
    # รับ DateObject มา แล้วส่งกลับเป็น timestamp
    return dateObj.timestamp()

def B4_cvDateObj2TimeStamp(dateObj):    
    
    # รับ DateObject มา แล้วส่งกลับเป็น dateString
    datetimeStr = dateObj.strftime("%d/%m/%Y, %H:%M:%S")
    return datetimeStr

def B5_dtstr_dtobject(datetime_str) :   
    
    datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
    return datetime_object

def B6_dtstr_timestamp(datetime_str):
    
    # datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S') 
    # datetime_object = datetime.strptime(datetime_str, '%d/%m/%y %H:%M:%S') 
    datetime_object = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M') 
    return datetime_object.timestamp()

def B24_dtstr_timestampLong(datetime_str):
    # B24_cvDateString2TimestampLong(starttimeText)
    # datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S') 
    # datetime_object = datetime.strptime(datetime_str, '%d/%m/%y %H:%M:%S') 
    datetime_object = datetime.strptime(datetime_str, '%d/%m/%ํY %H:%M:%S') 
    return datetime_object.timestamp()
    
    
        
# 1. หาเวลาปัจจุบัน แล้ว Return ได้ค่ากลับมาเป็น
#    -A1-timestamp
#    -A2-Object 
#    -A3-String
# 2. เปลี่ยนเวลาในรูปแบบต่างๆ 
    #  B1-timestamp->dateObject
    #  B2-timestamp->datetimestring  
    #  B3-dateObject->timestamp
    #  B4-dateObject->string
    #  B5-datetimestring->dateobject
    #  B6-datetimestring->timestamp

# now = time.time()
# tt = B1_cvTimestamp2Object(now)
# print(tt)

# tt2= B2_cvTimestamp2DateStr(now)
# print(tt2) 


# dateObj = A2_getCurrentObjectDateTime()
# print(dateObj)
# tt4  = B3_cvDateObj2TimeStamp(dateObj)
# print(tt4)

# datestr = B4_cvDateObj2TimeStamp(dateObj)
# print(datestr)

# # m/d/y
# datetime_str = '09/19/22 13:55:26'
# tt2 = B5_dtstr_dtobject(datetime_str)
# print(tt2) 

# tt3= B6_dtstr_timestamp(datetime_str)
# print(tt3)
