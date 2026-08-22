import pandas as pd
from .BaseStrategy import BaseStrategy

class MaCrossover(BaseStrategy):
    
    def __init__ (self, crossover_first, crossover_second):
            self.crossover_first = crossover_first
            self.crossover_second = crossover_second
    
    def generateSignals(self, df: pd.DataFrame, *args) -> pd.DataFrame:
        
        df = df.copy()
        df = df.sort_index()
        
        df = self._calculateCrossovers(df)
        
        df["Signal"] = pd.NA
            
        df["Signal"] = (df[f"Ma_{self.crossover_first}"] > df[f"Ma_{self.crossover_second}"]).astype(int)
        previous_signal = df["Signal"].shift(fill_value=0)
        df["Trade"] = (df["Signal"] - previous_signal).astype(int)
            
        
        df.dropna(inplace=True)
        
        return df
    
    def generateFeatures(self, df: pd.DataFrame) -> pd.DataFrame:
         
        df = self.generateSignals(df)
        df["Ma_signal"] = df["Signal"]
        
        short_col = f"Ma_{self.crossover_first}"
        long_col = f"Ma_{self.crossover_second}"
        df["Ma_spread_pct"] = ((df[short_col] - df[long_col]) / df["Close"])
        df["Ma_short_slope"] = (df[short_col].pct_change())
        df["Ma_long_slope"] = (df[long_col].pct_change())
        df["Ma_price_to_short"] = (df["Close"] - df[short_col]) / df[short_col]
        df["Ma_price_to_long"] = (df["Close"] - df[long_col]) / df[long_col]
        
        return df[["MA_spread_pct", "MA_short_slope", "MA_long_slope", "Price_to_short_MA", "Price_to_long_MA", "MA_signal"]]
         
    def _calculateCrossovers(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df[f"Ma_{self.crossover_first}"] = df["Close"].rolling(self.crossover_first).mean()
        df[f"Ma_{self.crossover_second}"] = df["Close"].rolling(self.crossover_second).mean()
        
        return df
    
    @classmethod
    def validateParameters(cls, params):
        
        short = params["crossover_first"]
        long = params["crossover_second"]
        
        return (
            isinstance(short, int)
            and isinstance (long, int)
            and short > 0
            and long > 0
            and short < long
        )
    
    