from .BaseStrategy import BaseStrategy
from ta.trend import MACD
import pandas as pd

class Macd(BaseStrategy):
    
    def __init__(self, window_fast = 12, window_slow = 26, window_signal = 9):
        
        self.window_fast = window_fast
        self.window_slow = window_slow
        self.window_signal = window_signal
        
    def _calculateMacd(self, df: pd.DataFrame) -> pd.DataFrame:
        
        macdIndicator = MACD(close = df["Close"], window_fast = self.window_fast, window_slow = self.window_slow, window_sign = self.window_signal)
        
        df["MACD"] = macdIndicator.macd()
        df["MACD_signal_line"] = macdIndicator.macd_signal()
        df["MACD_histogram"] = macdIndicator.macd_diff()
        
        return df
    
    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df = df.copy()
        df = df.sort_index()
        
        df = self._calculateMacd(df)
        
        df["Signal"] = (df["MACD"] > df["MACD_signal_line"]).astype(int)
        
        df["Trade"] = (df["Signal"].diff().fillna(df["Signal"]))
        
        df.dropna(inplace=True)
        
        return df
    
    def generateFeatures(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df = self._calculateMacd(df)
        
        df["MACD_pct"] = (
            df["MACD"] / df["Close"]
        )
        
        df["MACD_signal_pct"] = (
            df["MACD_signal_line"] / df["Close"]
        )

        df["MACD_histogram_pct"] = (
            df["MACD_histogram"] / df["Close"]
        )

        # Same state used by the strategy
        df["MACD_signal"] = (
            df["MACD"] > df["MACD_signal_line"]
        ).astype(int)

        return df[[
            "MACD_pct",
            "MACD_signal_pct",
            "MACD_histogram_pct",
            "MACD_signal"
        ]]


    @staticmethod
    def validateParameters(params):

        fast = params["window_fast"]
        slow = params["window_slow"]
        signal = params["window_signal"]

        return (
            isinstance(fast, int)
            and isinstance(slow, int)
            and isinstance(signal, int)
            and fast >= 2
            and slow >= 2
            and signal >= 2
            and fast < slow
        )