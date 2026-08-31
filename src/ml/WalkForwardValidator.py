import pandas as pd
from ml.MLPipeline import MLPipeline
from engine.Backtester import Backtester
import statistics


class WalkForwardValidator:

    def run(self, df: pd.DataFrame):

        pipeline = MLPipeline()
        splitPercentages = [0.2, 0.2, 0.2, 0.2, 0.2]

        dfFirst, dfSecond, dfThird, dfFourth, dfFifth = pipeline.splitData(
            df, splitPercentages
        )

        dfList = list(pipeline.splitData(df, splitPercentages))

        backtester = Backtester(inital_capital=100000, commission=0.0, slippage=0.0)

        dfCurrent = dfList[0]

        aucList = []
        
        resultList = []

        for validationIndex in range(1, len(dfList)):
            
            dfValidation = dfList[validationIndex]
            
            trainStart = dfCurrent.index[0]
            trainEnd = dfCurrent.index[-1]

            dfFoldResults, trainingAuc, validationAuc = pipeline.run(
                dfCurrent,
                dfList[validationIndex],
                backtester,
                "1d",
                predictionHorizon=5,
            )
            resultList.append(dfFoldResults)
            aucList.append(validationAuc)

            print(
                f"Fold {validationIndex}\n"
                f"Training AUC: {trainingAuc}\n"
                f"Validation AUC: {validationAuc}\n"
                f"Training: {dfCurrent.index[0]} -> {dfCurrent.index[-1]}\n"
                f"Validation: {dfList[validationIndex].index[0]} -> "
                f"{dfList[validationIndex].index[-1]}"
            )

            dfCurrent = pd.concat([dfCurrent, dfValidation])

        print(f"AUC mean: {statistics.mean(aucList)}")
        print(f"AUC std: {statistics.stdev(aucList)}")
        
        dfResults = pd.concat(resultList).sort_index()

        return dfResults
