import pandas as pd
from .BaseStrategy import BaseStrategy

class MaCrossover(BaseStrategy):
    
    def __init__ (self, crossover_first, crossover_second):
            self.crossover_first = crossover_first
            self.crossover_second = crossover_second
    
    def generateSignals(self, df: pd.DataFrame, *args) -> pd.DataFrame:
        
        df = df.copy()
        df = df.sort_index()
        
        df[f"Ma_{self.crossover_first}"] = df["Close"].rolling(self.crossover_first).mean()
        df[f"Ma_{self.crossover_second}"] = df["Close"].rolling(self.crossover_second).mean()
        
        df["Signal"] = pd.NA
            
        df["Signal"] = (df[f"Ma_{self.crossover_first}"] > df[f"Ma_{self.crossover_second}"]).astype(int)
        previous_signal = df["Signal"].shift(fill_value=0)
        df["Trade"] = (df["Signal"] - previous_signal).astype(int)
            
        
        df.dropna(inplace=True)
        
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
    
    