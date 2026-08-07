import pandas as pd
from .BaseStrategy import BaseStrategy

class BuyHold(BaseStrategy):
    
    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:
        
        df = df.copy()
        df = df.sort_index()
        
        df["Signal"] = 1
        df["Trade"] = 0
        df.iloc[0, df.columns.get_loc("Trade")] = 1
        
        df.dropna(inplace=True)
        
        return df
        
