import pandas as pd
from ml.MLPipeline import MLPipeline
from engine.Backtester import Backtester
import statistics


class WalkForwardValidator:

    def run(self, df: pd.DataFrame):

        pipeline = MLPipeline()
        splitPercentages = [0.4, 0.1, 0.1, 0.1, 0.1, 0.2]

        dfFirst, dfSecond, dfThird, dfFourth, dfFifth, dfSixth = pipeline.splitData(
            df, splitPercentages
        )

        dfList = [dfFirst, dfSecond, dfThird, dfFourth, dfFifth, dfSixth]

        backtester = Backtester(inital_capital=100000, commission=0.0, slippage=0.0)

        dfCurrent = dfList[0]

        aucList = []

        for validationIndex in range(1, len(dfList)):

            trainingAuc, validationAuc = pipeline.run(
                dfCurrent,
                dfList[validationIndex],
                backtester,
                "1d",
                predictionHorizon=5,
            )
            aucList.append(validationAuc)

            print(
                f"Fold {validationIndex}\n"
                f"Training AUC: {trainingAuc}\n"
                f"Validation AUC: {validationAuc}\n"
                f"Training: {dfCurrent.index[0]} -> {dfCurrent.index[-1]}\n"
                f"Validation: {dfList[validationIndex].index[0]} -> "
                f"{dfList[validationIndex].index[-1]}"
            )

            dfCurrent = pd.concat([dfCurrent, dfList[validationIndex]])

        print(f"AUC mean: {statistics.mean(aucList)}")
        print(f"AUC std: {statistics.stdev(aucList)}")
