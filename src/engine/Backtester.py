import pandas as pd
from pathlib import Path


class Backtester:
    
    def __init__(self, inital_capital = 100000):
        
        self.initial_capital = inital_capital
        
    def run(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy().sort_index()
        df["Trade_execution"] = df["Trade"].shift(1, fill_value=0)

        cash = self.initial_capital
        shares = 0

        for row in df.itertuples():
            price = row.Close
            trade_signal = row.Trade_execution

            if trade_signal == 1:
                shares_to_buy = int(cash // price)
                cash -= shares_to_buy * price
                shares += shares_to_buy

            elif trade_signal == -1:
                cash += shares * price
                shares = 0

            position_value = shares * price
            total_value = cash + position_value

            df.at[row.Index, "Shares"] = shares
            df.at[row.Index, "Cash"] = cash
            df.at[row.Index, "Position_value"] = position_value
            df.at[row.Index, "Total_value"] = total_value
            df.at[row.Index, "Portfolio_return"] = (total_value / self.initial_capital - 1) * 100

        df["Portfolio_return_1d%"] = df["Total_value"].pct_change().fillna(0) * 100
        
        return df
