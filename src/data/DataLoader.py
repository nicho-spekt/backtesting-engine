import yfinance as yf
import pandas as pd

class DataLoader:
    
    def __init__(self, ticker, start_date, end_date):
        
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date


    def loadData(self, interval) -> pd.DataFrame:

        data = yf.download(
            self.ticker,
            start=self.start_date,
            end=self.end_date,
            interval=interval,
            auto_adjust=True
        )
    
        if data.empty:
            raise ValueError(f"No data downloaded for {self.ticker}")
    
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data.index.name = "Date"
        
        return data