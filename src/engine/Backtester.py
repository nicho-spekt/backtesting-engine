import pandas as pd
import metrics_cpp


class Backtester:

    def __init__(self, inital_capital = 100000, commission = 0.0, slippage = 0.0):
        self.initial_capital = inital_capital
        self.commission = commission
        self.slippage = slippage

    def run(self, df: pd.DataFrame, execution_delay = 1) -> pd.DataFrame:

        df = df.copy().sort_index()

        df["Trade_execution"] = df["Trade"].shift(execution_delay,fill_value=0)

        prices = (df["Close"].astype(float).tolist())

        trades = (df["Trade_execution"].astype(int).tolist())

        result = metrics_cpp.runBacktest(prices, trades, self.initial_capital, self.commission, self.slippage)

        df["Shares"] = result.shares
        df["Cash"] = result.cash
        df["Position_value"] = result.position_values
        df["Total_value"] = result.total_values
        df["Portfolio_return"] = result.portfolio_returns
        df["Portfolio_return_period"] = result.portfolio_return_period

        return df