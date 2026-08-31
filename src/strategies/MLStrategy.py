from ml.MLPipeline import MLPipeline
from engine.Backtester import Backtester
import pandas as pd


class MLStrategy():

    def __init__(self, probabilityThreshold=0.5):

        self.probabilityThreshold = probabilityThreshold

    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()
        df = df.sort_index()

        df["Signal"] = (df["Probability"] >= self.probabilityThreshold).astype(int)

        previousSignal = df["Signal"].shift(fill_value=0)

        df["Trade"] = (df["Signal"] - previousSignal).astype(int)

        return df
