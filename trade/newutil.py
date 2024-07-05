from datetime import datetime
import time

def cv_TimeStamp_DateTime(timestamp1) :
    
    timestring = ''
    dt_object = datetime.fromtimestamp(timestamp1)
    
    return dt_object

def cv_DateTimeObj_TimeStamp(dateTimeObj):
    
    TimeStamp1 = datetime.timestamp(dateTimeObj)
    
    return TimeStamp1
    
def getCurrentDateTime():    
    return datetime.now()

def getCurrentDateTimeStamp():    
    return datetime.now().timestamp()

def cv_String_DateTimeObj(date_str):
    
    # date_str = '2023-02-28 14:30:00'
    date_format = '%Y-%m-%d %H:%M:%S'
    date_obj = datetime.strptime(date_str, date_format)
    
    return date_obj 

def cv_String_DateTimeStamp(date_str):
    
    # date_str = '2023-02-28 14:30:00'
    date_format = '%Y-%m-%d %H:%M:%S'
    date_obj = datetime.strptime(date_str, date_format)
    TimeStamp1 = datetime.timestamp(date_obj)
    
    
    return TimeStamp1

def cv_Object_DateTimeString(date_obj):
    
    # date_str = '2023-02-28 14:30:00'
    #date_str = date_obj.strftime("%m/%d/%Y, %H:%M:%S")
    date_str = date_obj.strftime("%Y-%m-%d, %H:%M:%S")
    
    
    
    return date_str

def DiffDateTimeString():
    
    

    return ''

def AddTimeWithMinute(dateObj,SecondsAdd):
    
   thisTimeStamp = cv_DateTimeObj_TimeStamp(dateObj)  
   print('ThisTimeStamp',thisTimeStamp)
   TimeStampAdded   = thisTimeStamp + (SecondsAdd*60)
   
   print('TimeStamp Added ',TimeStampAdded)
   
   DateTimeAdd= cv_TimeStamp_DateTime(TimeStampAdded)
   
   

   return DateTimeAdd  

# current = getCurrentDateTime()
# currentTimestamp = cv_DateTime_TimeStamp(current)
# print('Current DateTime=',getCurrentDateTime())
# print('Current TimeStamp=',getCurrentDateTimeStamp())

# print(cv_String_DateTimeObj())
# print(cv_String_DateTimeStamp())


# startTime = time.time()
# print(startTime)
# sdateTime = cv_TimeStamp_DateTime(startTime)
# print(sdateTime)
