from ml.MLPipeline import MLPipeline
from engine.Backtester import Backtester
import pandas as pd


class MLStrategy:

    def __init__(self, probabilityThreshold=0.5, holdingPeriod=5):

        self.probabilityThreshold = probabilityThreshold,
        self.holdingPeriod = holdingPeriod

    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()
        df = df.sort_index()

        nHoldingDays = 0
        
        df["Signal"] = 0

        #df["Signal"] = (df["Probability"] >= self.probabilityThreshold).astype(int)

        for row in df.itertuples():

            if df.at[row.Index, "Probability"] >= self.probabilityThreshold and nHoldingDays == 0:

                nHoldingDays = self.holdingPeriod
                df.at[row.Index, "Signal"] = 1

            if nHoldingDays > 0:

                df.at[row.Index, "Signal"] = 1
                nHoldingDays -= 1

        previousSignal = df["Signal"].shift(fill_value=0)

        df["Trade"] = (df["Signal"] - previousSignal).astype(int)

        return df
