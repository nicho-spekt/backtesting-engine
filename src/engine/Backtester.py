import pandas as pd

class Backtester:
    
    def __init__(self, inital_capital = 100000, commission=0.0, slippage=0.0):
        
        self.initial_capital = inital_capital
        self.commission = commission
        self.slippage = slippage
        
    def run(self, df: pd.DataFrame, execution_delay = 1) -> pd.DataFrame:

        df = df.copy().sort_index()
        df["Trade_execution"] = df["Trade"].shift(execution_delay, fill_value=0)

        cash = self.initial_capital
        shares = 0

        for row in df.itertuples():
            price = row.Close
            trade_signal = row.Trade_execution

            if trade_signal == 1:
                execution_price = price * (1 + self.slippage)
                shares_to_buy = int((cash - self.commission) // execution_price)
                cash -= shares_to_buy * execution_price + self.commission
                shares += shares_to_buy

            elif trade_signal == -1:
                execution_price = price * (1 - self.slippage)
                cash += shares * execution_price - self.commission
                shares = 0

            position_value = shares * price
            total_value = cash + position_value

            df.at[row.Index, "Shares"] = shares
            df.at[row.Index, "Cash"] = cash
            df.at[row.Index, "Position_value"] = position_value
            df.at[row.Index, "Total_value"] = total_value
            df.at[row.Index, "Portfolio_return"] = (total_value / self.initial_capital - 1) * 100

        df["Portfolio_return_period%"] = df["Total_value"].pct_change().fillna(0)
        
        return df
