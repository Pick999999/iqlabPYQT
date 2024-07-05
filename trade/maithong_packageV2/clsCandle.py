import json
from dataclasses import dataclass
import mylib 


# JSON ต้นแบบ
json_data = '''
{
    "curpair": "EURUSD-OTC",  
    "dataMultiply" : 1000000,
    "candleCode": "WD",
    "minuteno": 123,
    "RawData": {
        "id": 3378731,        
        "from": 1713648720,
        "at": 1713648780000000000,
        "to": 1713648780,
        "open": 1.071075,
        "close": 1.071075,
        "min": 1.071055,
        "max": 1.071135,
        "volume": 0
    },
    "bodyData": {
        "Color": "Green",
        "CandleHeight": 0.0,
        "BodyHeight": 0.0,
        "UHeight": 0.0,
        "LHeight": 0.0,
        "BodyHeightPercent": 0.0,
        "UHeightPercent": 0.0,
        "LHeightPercent": 0.0,
        "CandleType": "Doji"
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
            "emaConflict" : "Yes",
            "ConvergenceType": 0.0,
            "ConvergenceType": "Conv",
            "TurnPointType": "T2Down",
            "IdOfLastTurnPoint": "12345",
            "TurnPointNo": 11,
            "CutPointType": "3cut5"
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
        "action": "CALL",
        "MoneyTrade": 2,
        "profit": 0.0,
        "balance": 0.0
    }
}
'''

# สร้างคลาสจาก JSON ต้นแบบ
@dataclass
class Candle:
    curpair: str
    dataMultiply: int
    candleCode: str
    minuteno: int
    RawData: dict
    bodyData: dict
    macd: dict
    Bollinger: dict
    RSI: dict
    atr: dict
    trade: dict

    # เพิ่มเมธอดใหม่
    def display_info(self):
        print(f"Currency Pair: {self.curpair}")
        print(f"Candle Code: {self.candleCode}")
        print(f"Minuteno: {self.minuteno}")
        print("Raw Data:")
        for key, value in self.RawData.items():
            print(f"    {key}: {value}")
        print("Body Data:")
        for key, value in self.bodyData.items():
            print(f"    {key}: {value}")
        print("MACD:")
        for key, value in self.macd.items():
            if key == "analysis":
                print("    Analysis:")
                for k, v in value.items():
                    print(f"        {k}: {v}")
            else:
                print(f"    {key}: {value}")
        print("Bollinger:")
        for key, value in self.Bollinger.items():
            print(f"    {key}: {value}")
        print("RSI:")
        for key, value in self.RSI.items():
            print(f"    {key}: {value}")
        print("ATR:")
        for key, value in self.atr.items():
            print(f"    {key}: {value}")
        print("Trade:")
        for key, value in self.trade.items():
            print(f"    {key}: {value}")
    
    def CandleWarning(self): 
        
        print('------>',self.curpair)
    
    def setCurpair(self,newCurPair):
        
        self.curpair = newCurPair
        
    def getRawData(self,I_want_money,timeserver,numcandle) :
        
        rawcandleList= mylib.getCandleByFirstRound(I_want_money, self.curpair,  numcandle)
        # print(rawcandleList)
        pass 
        return timeserver     
    
    
        
    
# แปลง JSON เป็น dictionary
data_dict = json.loads(json_data)

# สร้างออบเจกต์จากคลาส Candle
candle = Candle(**data_dict)

# เรียกใช้งานเมธอด display_info()
# candle.display_info()
candle.CandleWarning()
