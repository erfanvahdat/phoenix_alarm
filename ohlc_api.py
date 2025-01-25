

import pytz
import requests
import pandas as pd
import yfinance as yf
from ta import momentum    
from datetime import datetime,timedelta



def mexi(ticker,limit,timeframe):
    try:
        ticker = ticker.upper()
        response = requests.get(f'https://api.mexc.co/api/v3/klines?symbol={ticker}USDT&interval={timeframe}m&limit={limit}')
        df= pd.DataFrame(response.json())

        # df.index = pd.to_datetime(df.iloc[:, 0], unit='ms')   

        df.index=[datetime.fromtimestamp(float(i) / 1e3)   for i in df.iloc[:,0] ]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset']
        df = df[[ 'Open', 'High', 'Low', 'Close', 'Volume' ]].astype(float)
        df.loc[:,"Time"]  =df.index
        # Calculate RSI
        df['rsi'] = momentum.rsi(df['Close'], window=14)

        return df
       
    except:
        print(ticker+' does not exit')


def kucoin_data(symbol: str,num_timeframe : int,format_timeframe: str ,past_time:int=100):
        """ gets kucoin data and convert to dataframe """

        start = datetime.timestamp(datetime.now()- timedelta(days=past_time))

        ticker=f"{symbol}-usdt".upper()
        data=requests.get(f"https://api.kucoin.com/api/v1/market/candles?type={num_timeframe}{format_timeframe}&symbol={ticker}&startAt={int(start)}").json()
        
        if "data" in data.keys():
            data=pd.DataFrame(data)["data"]
            data=pd.DataFrame(list(data))

            if not data.empty:
                data.columns=["Time","Open","Close","High","Low","Volume","CloseTime"]
                data["Time"]=data["Time"].astype(float)
                data=data.astype('float')
                data["Time"]=pd.to_datetime(data["Time"],unit="s")
                data['Time'] = pd.to_datetime(data["Time"],unit="s").dt.tz_localize('UTC').dt.tz_convert('Asia/Tehran')
                
                data["Symbol"]=ticker
                data_df=pd.DataFrame(data)
                data_df= data_df.sort_values(by='Time',ascending=True)
                data_df['rsi']=momentum.rsi( close = data_df['Close'],window= 14)
                data_df.index = data_df['Time']
                return data_df

def forex(ticker):

    ticker= ticker.upper()
    one_day= timedelta(days=1)
    start= datetime.strftime(datetime.now() - one_day ,format='%Y-%m-%d')
    end= datetime.strftime(datetime.now(),format='%Y-%m-%d')

    
    data= yf.download(ticker, start=None, end=None, actions=False, threads=True, ignore_tz=None,
             group_by='column', auto_adjust=False, back_adjust=False, repair=False, keepna=False,
             progress=True, period="5d", interval="1m", prepost=False,
             proxy = None, rounding=False, timeout=10, session=None)

    data.loc[:,'Time'] =data.index
    data.loc[:,'Time']=[ i.astimezone(pytz.timezone('Asia/Tehran'))  for  i in data['Time']]
    data.index= data['Time']
    
    return  data 


# print(kucoin_data(format_timeframe='min',num_timeframe=1 ,symbol= 'btc',))

# print(mexi(ticker='btc',limit=100))


# ticker= 'USDJPY=X'
# a  = forex(ticker=ticker)
