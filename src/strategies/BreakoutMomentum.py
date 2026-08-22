import pandas as pd
from .BaseStrategy import BaseStrategy

class BreakoutMomentum(BaseStrategy):
    
    def __init__ (self, window_high, window_low):
        self.window_high = window_high
        self.window_low = window_low
    
    def generateSignals(self, df: pd.DataFrame, *args) -> pd.DataFrame:
        
        df = df.copy()
        df = df.sort_index()
    
        df = self._calculatePriceActionLines(df)
    
        df["Signal"] = pd.NA
    
        df.loc[df["Close"] > df["Breakout_High"], "Signal"] = 1
        df.loc[df["Close"] < df["Exit_Low"], "Signal"] = 0
        
        df["Signal"] = df["Signal"].ffill().fillna(0).astype(int)
        previous_signal = df["Signal"].shift(fill_value=0)
        df["Trade"] = (df["Signal"] - previous_signal).astype(int)
    
        df.dropna(inplace=True)
        
        return df
    
    def generateFeatures(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df = self.generateSignals(df)
        df["Breakout_signal"] = df["Signal"]
        
        df["Breakout_distance_high"] = (df["Close"] / df["Breakout_High"] - 1.0)
        df["Breakout_distance_low"] = (df["Close"] / df["Exit_Low"] - 1.0)
        df["Breakout_channel_width"] = (df["Breakout_High"] - df["Exit_Low"]) / df["Close"]
        df["Breakout_strength"] = (df["Close"] - df["Breakout_High"]) / df["Breakout_High"]
        
        return df[["Breakout_distance_high", "Breakout_distance_low", "Breakout_channel_width", "Breakout_signal"]]
        
    
    def _calculatePriceActionLines(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df["Breakout_High"] = df["Close"].rolling(self.window_high).max().shift(1)
        df["Exit_Low"] = df["Close"].rolling(self.window_low).min().shift(1)
        
        return df
    
    @classmethod
    def validateParameters(cls, params):
        
        high = params["window_high"]
        low = params["window_low"]
        
        return(
            isinstance(high, int)
            and isinstance(low, int)
            and high >= 2
            and low >= 2
            and low < high
        )