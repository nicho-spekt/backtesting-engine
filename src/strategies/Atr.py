from ta.volatility import AverageTrueRange
import pandas as pd


class Atr:

    def __init__(self, window=14):
        self.window = window

    def generateFeatures(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy().sort_index()

        atrIndicator = AverageTrueRange(
            high=df["High"], low=df["Low"], close=df["Close"], window=self.window
        )

        df["ATR"] = atrIndicator.average_true_range()

        df["ATR_pct"] = df["ATR"] / df["Close"]

        df["ATR_change"] = df["ATR"].pct_change()

        df["ATR_ratio"] = df["ATR"] / df["ATR"].rolling(20).mean()

        return df[["ATR_pct", "ATR_change", "ATR_ratio"]]
