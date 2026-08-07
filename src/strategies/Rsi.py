import pandas as pd
from ta.momentum import RSIIndicator
from .BaseStrategy import BaseStrategy

class Rsi(BaseStrategy):
    
    def __init__ (self, window, lower_std_threshold, upper_std_threshold):
        self.window = window
        self.lower_std_threshold = lower_std_threshold
        self.upper_std_threshold = upper_std_threshold
    
    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df = df.copy()
        df = df.sort_index()
        
        df['RSI'] = RSIIndicator(close=df['Close'], window=self.window).rsi()
        df['Signal'] = pd.NA
            
        df.loc[df["RSI"] < self.lower_std_threshold, "Signal"] = 1
        df.loc[df["RSI"] > self.upper_std_threshold, "Signal"] = 0
            
        df["Signal"] = df["Signal"].ffill().fillna(0).astype(int)
        previous_signal = df["Signal"].shift(fill_value=0)
        df["Trade"] = (df["Signal"] - previous_signal).astype(int)
            
            
        df.dropna(inplace=True)
        
        return df