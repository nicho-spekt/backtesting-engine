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
            
        df = self._calculateBollingerBands(df)
        
        df["Signal"] = pd.NA
            
        df.loc[df["Close"] < df["BB_Lower"], "Signal"] = 1
        df.loc[df["Close"] > df["BB_Middle"], "Signal"] = 0
            
        df["Signal"] = df["Signal"].ffill().fillna(0).astype(int)
        previous_signal = df["Signal"].shift(fill_value=0)
        df["Trade"] = (df["Signal"] - previous_signal).astype(int)
            
        df.dropna(inplace=True)
            
        return df
    
    def generateFeatures(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df = self.generateSignals(df)
        df["BB_signal"] = df["Signal"]         
        
        df["BB_percent_b"] = ((df["Close"] - df["BB_Lower"]) / (df["BB_Upper"] - df["BB_Lower"]))
        df["BB_bandwith"] - ((df["BB_Upper"] - df["BB_Lower"]) / df["BB_Middle"])
        df["BB_distance_middle"] = ((df["Close"] - df["BB_Middle"]) / df["BB_Middle"])
        df["BB_bandwith_change"] = (df["BB_bandwith"].pct_change())
        
        return df[["BB_percent_b", "BB_bandwidth", "BB_distance_middle", "BB_bandwidth_change", "BB_signal"]]
        
    def _calculateBollingerBands(self, df: pd.DataFrame):
        
        indicator_bb = TaBollingerBands(close=df["Close"], window=self.window, window_dev=self.window_dev)
        df["BB_Middle"] = indicator_bb.bollinger_mavg()
        df["BB_Upper"] = indicator_bb.bollinger_hband()
        df["BB_Lower"] = indicator_bb.bollinger_lband()
        
        return df
    
    @classmethod
    def validateParameters(cls, params):
        
        window = params["window"]
        deviation = params["window_dev"]
    
        return(
            isinstance(window, int)
            and window >= 2
            and deviation > 0
        )