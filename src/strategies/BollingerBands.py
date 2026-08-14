from ta.volatility import BollingerBands as TaBollingerBands
import pandas as pd
from .BaseStrategy import BaseStrategy

class BollingerBands(BaseStrategy):
    
    def __init__ (self, window, window_dev):
        self.window = window
        self.window_dev = window_dev
    
    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df = df.copy()
        df = df.sort_index()
            
        indicator_bb = TaBollingerBands(close=df["Close"], window=self.window, window_dev=self.window_dev)
            
        df["BB_Middle"] = indicator_bb.bollinger_mavg()
        df["BB_Upper"] = indicator_bb.bollinger_hband()
        df["BB_Lower"] = indicator_bb.bollinger_lband()
        
        df["Signal"] = pd.NA
            
        df.loc[df["Close"] < df["BB_Lower"], "Signal"] = 1
        df.loc[df["Close"] > df["BB_Middle"], "Signal"] = 0
            
        df["Signal"] = df["Signal"].ffill().fillna(0).astype(int)
        previous_signal = df["Signal"].shift(fill_value=0)
        df["Trade"] = (df["Signal"] - previous_signal).astype(int)
            
        df.dropna(inplace=True)
            
        return df
    
    @classmethod
    def validateParameters(cls, params):
        
        window = params["window"]
        deviation = params["window_dev"]
        
        return(
            isinstance(window, int)
            and isinstance(deviation, int)
            and window >= 2
            and deviation > 0
        )