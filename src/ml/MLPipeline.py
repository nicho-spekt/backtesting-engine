import pandas as pd
from optimization.ParameterOptimizer import ParameterOptimizer
from ml.FeatureEngine import FeatureEngine
from ml.ModelTrainer import ModelTrainer

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    confusion_matrix,
    roc_auc_score,
    balanced_accuracy_score,
)


class MLPipeline:

    # def run(self, df: pd.DataFrame, backtester, listPercentages: list[float], interval="1d", predictionHorizon=1):
    def run(
        self,
        dfTrain: pd.DataFrame,
        dfValidation: pd.DataFrame,
        backtester,
        interval="1d",
        predictionHorizon=1,
    ):

        # dfTrain, dfValidation, dfTest = self.splitData(df, listPercentages)

        optimizer = ParameterOptimizer()
        optimizedParams = optimizer.optimizeAllStrategies(dfTrain, backtester, interval)

        featureEngine = FeatureEngine()

        df = pd.concat([dfTrain, dfValidation])

        dfAllFeatures = featureEngine.run(
            df, optimizedParams, interval, predictionHorizon, 0.025
        )

        trainEndIndex = dfTrain.index[-1]
        validationEndIndex = dfValidation.index[-1]

        dfTrainFeatures = dfAllFeatures.loc[dfAllFeatures.index <= trainEndIndex]
        dfValidationFeatures = dfAllFeatures.loc[
            (dfAllFeatures.index > trainEndIndex)
            & (dfAllFeatures.index <= validationEndIndex)
        ]

        dfTestFeatures = dfAllFeatures.loc[dfAllFeatures.index > validationEndIndex]

        dfTrainFeatures = dfTrainFeatures.iloc[:-predictionHorizon]
        dfValidationFeatures = dfValidationFeatures.iloc[:-predictionHorizon]

        featureColumns = FeatureEngine.getFeatureColumns()

        dfXTrain = dfTrainFeatures[featureColumns]
        dfYTrain = dfTrainFeatures["Target"].astype(int)

        dfXValidation = dfValidationFeatures[featureColumns]
        dfYValidation = dfValidationFeatures["Target"].astype(int)

        print(
            f"\n==========Rates==========\n"
            f"Training positive rate: {dfYTrain.mean()}\n"
            f"Validation postive rate: {dfYValidation.mean()}\n"
            f"\n==========Rates==========\n"
        )

        featureShift = (
            ((dfXValidation.mean() - dfXTrain.mean()) / dfXTrain.std())
            .abs()
            .sort_values(ascending=False)
        )

        """print("\n==============================")
        print("LARGEST TRAIN-VALIDATION FEATURE SHIFTS")
        print("==============================")
        print(featureShift.head(15))
        print("==============================\n")"""

        modelTrainer = ModelTrainer(modelType="logistic")

        modelTrainer.train(dfXTrain, dfYTrain)

        # coefficients = modelTrainer.getCoefficients(dfXTrain.columns)

        """print("\n==============================")
        print("MODEL COEFFICIENTS")
        print("==============================")
        print(coefficients)
        print("==============================\n")"""

        predictions = modelTrainer.predict(dfXValidation)
        probabilities = modelTrainer.predictProbabilities(dfXValidation)

        trainPredictions = modelTrainer.predict(dfXTrain)

        trainProbabilities = modelTrainer.predictProbabilities(dfXTrain)

        """print("\n==============================")
        print("ML TRAINING RESULTS")
        print("==============================")

        print("Accuracy:", accuracy_score(dfYTrain, trainPredictions))

        print("Precision:", precision_score(dfYTrain, trainPredictions))

        print("Recall:", recall_score(dfYTrain, trainPredictions))"""

        trainingAuc = roc_auc_score(dfYTrain, trainProbabilities)

        """print("ROC AUC:", trainingAuc)

        print("Balanced accuracy:", balanced_accuracy_score(dfYTrain, trainPredictions))

        print("Positive rate:", dfYTrain.mean())

        print("Predicted positive rate:", trainPredictions.mean())

        print("==============================")"""

        accuracy = accuracy_score(dfYValidation, predictions)

        precision = precision_score(dfYValidation, predictions)

        recall = recall_score(dfYValidation, predictions)

        validationAuc = roc_auc_score(dfYValidation, probabilities)

        matrix = confusion_matrix(dfYValidation, predictions)

        """ print("\n==============================")
        print("ML VALIDATION RESULTS")
        print("==============================")

        print("Accuracy:", accuracy)
        print("Precision:", precision)
        print("Recall:", recall)
        print("ROC AUC:", validationAuc)

        print("\nConfusion Matrix:")
        print(matrix)

        print("Positive rate:", dfYValidation.mean())

        print("Predicted positive rate:", predictions.mean())

        print("Balanced accuracy:", balanced_accuracy_score(dfYValidation, predictions))

        print("Average predicted probability:", probabilities.mean())

        print("Min probability:", probabilities.min())

        print("Max probability:", probabilities.max())

        # coefficients = modelTrainer.getCoefficients(
        # dfXTrain.columns
        # )

        # print("\nModel coefficients:")
        # print(coefficients)

        print("==============================\n")"""

        return trainingAuc, validationAuc

    def splitData(self, df: pd.DataFrame, percentages: list[float]):

        assert len(percentages) > 0
        assert all(isinstance(p, (int, float)) for p in percentages)
        assert all(p > 0 for p in percentages)
        assert all(p <= 1 for p in percentages)
        assert abs(sum(percentages) - 1.0) < 1e-9

        previousPercentage, previousSplit, currentPercentage, currentSplit = (
            0.0,
            0,
            0.0,
            0,
        )

        for index, percentage in enumerate(percentages):

            if index == len(percentages) - 1:
                dfSplit = df.iloc[previousSplit:]
            else:
                currentPercentage = previousPercentage + percentage
                currentSplit = int(len(df) * currentPercentage)
                dfSplit = df.iloc[previousSplit:currentSplit]
                previousPercentage = currentPercentage
                previousSplit = currentSplit

            yield dfSplit
