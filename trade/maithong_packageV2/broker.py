import sys
from iqoptionapi.stable_api import IQ_Option 



def getIQ() :
    
    username = 'nutv99@gmail.com' ; passw = 'Maithong11181'
    I_want_money = IQ_Option(username,passw) 
    check, reason=  I_want_money.connect()
    
    if check == False:
       print('ไม่สามารถ Connect IQOption ได้ ' , reason ) 
       sys.exit(0)
    else : 
       if check:   
          print('Connect IQOption สำเร็จ ' ) 
          return I_want_money
 
def IQ_CheckCurpair_OpenedBinary(iqoption):
    
    # Get all available active pairs
    iqoption.update_ACTIVES_OPCODE()
    active_pairs = iqoption.get_all_ACTIVES_OPCODE()

    # Print the structure of active_pairs to understand it better
    print("Active pairs structure:")
    for pair, data in active_pairs.items():
        print(pair, data)

    # Filter out binary options that are currently open for trade
    open_binary_options = {pair: data for pair, data in active_pairs.items() if isinstance(data, dict) and data.get("binary", {}).get("open", False)}

    # Print the open binary options
    if open_binary_options:
        no = 1
        print("Open binary options for trading:")
        for pair, data in open_binary_options.items():
            print(no) ; no = no+1
            print(f"{pair}: {data}")
    else:
        print("No binary options are currently open for trading.")