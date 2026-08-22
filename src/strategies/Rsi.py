import pandas as pd
from ta.momentum import RSIIndicator
from .BaseStrategy import BaseStrategy

class Rsi(BaseStrategy):
    
    _rsiCache = {}
    
    def __init__ (self, window, lower_std_threshold, upper_std_threshold):
        self.window = window
        self.lower_std_threshold = lower_std_threshold
        self.upper_std_threshold = upper_std_threshold
    
    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df = df.copy()
        df = df.sort_index()
        
        df = self._calculateRsi(df)
        df['Signal'] = pd.NA
            
        df.loc[df["RSI"] < self.lower_std_threshold, "Signal"] = 1
        df.loc[df["RSI"] > self.upper_std_threshold, "Signal"] = 0
            
        df["Signal"] = df["Signal"].ffill().fillna(0).astype(int)
        previous_signal = df["Signal"].shift(fill_value=0)
        df["Trade"] = (df["Signal"] - previous_signal).astype(int)
            
            
        df.dropna(inplace=True)
        
        return df
    
    def generateFeatures(self, df:pd.DataFrame) -> pd.DataFrame:
        
        df = self.generateSignals(df)
        df["RSI_signal"] = df["Signal"]
        
        df["RSI_value"] = df["RSI"]
        df["RSI_centered"] = ((df["RSI"] - 50.0) / 50.0)
        df["RSI_change"] = (df["RSI"].diff())
        df["RSI_distance_lower"] = (df["RSI"] - self.lower_std_threshold) / self.lower_std_threshold
        df["RSI_distance_upper"] = (self.upper_std_threshold - df["RSI"]) / self.upper_std_threshold
        
        return df[["RSI_value", "RSI_centered", "RSI_change", "RSI_distance_lower", "RSI_distance_upper", "RSI_signal"]]
    
    def _calculateRsi(self, df: pd.DataFrame) -> pd.DataFrame:
        
        cacheKey = (self.window, df.index[0], df.index[-1], len(df))
        
        if cacheKey not in Rsi._rsiCache:
            Rsi._rsiCache[self.window] = RSIIndicator(close=df['Close'], window=self.window).rsi()
            
        df['RSI'] = Rsi._rsiCache[self.window]
        
        return df
    
    @classmethod
    def validateParameters(cls, params):
        
        window = params["window"]
        lower = params["lower_std_threshold"]
        upper = params["upper_std_threshold"]
        
        return(
            isinstance(window, int)
            and window >= 2
            and 0 <= lower <= 100
            and 0 <= upper <= 100
            and lower < upper
        )