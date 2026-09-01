import pandas as pd
from ml.MLPipeline import MLPipeline
from engine.Backtester import Backtester
import statistics
from strategies.MLStrategy import MLStrategy
from analytics.MetricsCalculator import MetricsCalculator


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

            dfFoldResults = dfFoldResults.copy()
            dfFoldResults["Fold"] = validationIndex
            resultList.append(dfFoldResults)
            aucList.append(validationAuc)

            print("\n")
            print("=" * 60)
            print(f"FOLD {validationIndex}")
            print("=" * 60)

            print(f"Training:   {trainStart.date()} -> {trainEnd.date()}")

            print(
                f"Validation: {dfValidation.index[0].date()} -> "
                f"{dfValidation.index[-1].date()}"
            )

            print(f"Training AUC:   {trainingAuc:.4f}")

            print(f"Validation AUC: {validationAuc:.4f}")

            dfCurrent = pd.concat([dfCurrent, dfValidation])

        dfResults = pd.concat(resultList).sort_index()

        print("\n")
        print("=" * 60)
        print("MODEL WALK-FORWARD SUMMARY")
        print("=" * 60)

        print(f"Mean validation AUC: " f"{statistics.mean(aucList):.4f}")

        print(f"Validation AUC std:  " f"{statistics.stdev(aucList):.4f}")

        # ==========================================
        # 2. TEST PROBABILITY THRESHOLDS
        # ==========================================

        thresholds = [
            0.100,
            0.110,
            0.115,
            0.120,
            0.125,
            0.130,
            0.135,
            0.140,
            0.145,
            0.150
        ]

        for threshold in thresholds:

            returnList = []
            sharpeList = []
            drawdownList = []
            tradesList = []
            investedList = []

            print("\n\n")
            print("#" * 60)
            print(f"ML STRATEGY - THRESHOLD {threshold:.4f}")
            print("#" * 60)

            for fold in sorted(dfResults["Fold"].unique()):

                dfFold = dfResults[dfResults["Fold"] == fold].copy()

                strategy = MLStrategy(probabilityThreshold=threshold)

                dfSignals = strategy.generateSignals(dfFold)

                backtester = Backtester(
                    inital_capital=100000, commission=0.0, slippage=0.0
                )

                # ML signal from day t executes at t+1
                dfPortfolio = backtester.run(dfSignals, 1)

                metrics = MetricsCalculator()

                dfMetrics = metrics.calculateMetrics(dfPortfolio, "1d")

                result = dfMetrics.iloc[0]

                cumulativeReturn = result["Cumulative_return"]

                sharpe = result["Sharpe_ratio"]

                maxDrawdown = result["Max_drawdown"]

                numberTrades = int(result["Number_of_trades"])

                timeInvested = result["Time_invested"]

                returnList.append(cumulativeReturn)

                sharpeList.append(sharpe)

                drawdownList.append(maxDrawdown)

                tradesList.append(numberTrades)

                investedList.append(timeInvested)

                print(f"\nFold {fold}")

                print(
                    f"Dates:           "
                    f"{dfFold.index[0].date()} -> "
                    f"{dfFold.index[-1].date()}"
                )

                print(f"Ending value:    " f"${result['Ending_value']:,.2f}")

                print(f"Return:          " f"{cumulativeReturn * 100:.2f}%")

                print(f"Sharpe:          " f"{sharpe:.3f}")

                print(f"Max drawdown:    " f"{maxDrawdown * 100:.2f}%")

                print(f"Trades:          " f"{numberTrades}")

                print(f"Time invested:   " f"{timeInvested * 100:.2f}%")

            # ======================================
            # THRESHOLD SUMMARY
            # ======================================

            print("\n")
            print("-" * 60)
            print(f"THRESHOLD {threshold:.4f} SUMMARY")
            print("-" * 60)

            print(f"Mean return:        " f"{statistics.mean(returnList) * 100:.2f}%")

            print(f"Mean Sharpe:        " f"{statistics.mean(sharpeList):.3f}")

            print(f"Mean max drawdown:  " f"{statistics.mean(drawdownList) * 100:.2f}%")

            print(f"Mean trades:        " f"{statistics.mean(tradesList):.1f}")

            print(f"Mean time invested: " f"{statistics.mean(investedList) * 100:.2f}%")

        # ==========================================
        # 3. BUY & HOLD BENCHMARK PER FOLD
        # ==========================================

        from strategies.BuyHold import BuyHold

        buyHoldReturnList = []
        buyHoldSharpeList = []
        buyHoldDrawdownList = []

        print("\n\n")
        print("#" * 60)
        print("BUY & HOLD BENCHMARK")
        print("#" * 60)

        for fold in sorted(dfResults["Fold"].unique()):

            dfFold = dfResults[dfResults["Fold"] == fold].copy()

            buyHold = BuyHold()

            dfBuyHoldSignals = buyHold.generateSignals(dfFold)

            backtester = Backtester(inital_capital=100000, commission=0.0, slippage=0.0)

            dfBuyHoldPortfolio = backtester.run(
                dfBuyHoldSignals, buyHold.execution_delay
            )

            metrics = MetricsCalculator()

            dfBuyHoldMetrics = metrics.calculateMetrics(dfBuyHoldPortfolio, "1d")

            result = dfBuyHoldMetrics.iloc[0]

            cumulativeReturn = result["Cumulative_return"]

            sharpe = result["Sharpe_ratio"]

            maxDrawdown = result["Max_drawdown"]

            buyHoldReturnList.append(cumulativeReturn)

            buyHoldSharpeList.append(sharpe)

            buyHoldDrawdownList.append(maxDrawdown)

            print(f"\nFold {fold}")

            print(
                f"Dates:           "
                f"{dfFold.index[0].date()} -> "
                f"{dfFold.index[-1].date()}"
            )

            print(f"Ending value:    " f"${result['Ending_value']:,.2f}")

            print(f"Return:          " f"{cumulativeReturn * 100:.2f}%")

            print(f"Sharpe:          " f"{sharpe:.3f}")

            print(f"Max drawdown:    " f"{maxDrawdown * 100:.2f}%")

        print("\n")
        print("-" * 60)
        print("BUY & HOLD SUMMARY")
        print("-" * 60)

        print(f"Mean return:       " f"{statistics.mean(buyHoldReturnList) * 100:.2f}%")

        print(f"Mean Sharpe:       " f"{statistics.mean(buyHoldSharpeList):.3f}")

        print(
            f"Mean max drawdown: " f"{statistics.mean(buyHoldDrawdownList) * 100:.2f}%"
        )

        return dfResults
