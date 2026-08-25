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

    def run(self, df: pd.DataFrame, backtester, interval="1d", predictionHorizon=1):

        dfTrain, dfValidation, dfTest = self.splitData(df)

        optimizer = ParameterOptimizer()
        optimizedParams = optimizer.optimizeAllStrategies(dfTrain, backtester, interval)

        featureEngine = FeatureEngine()

        dfAllFeatures = featureEngine.run(
            df, optimizedParams, interval, predictionHorizon
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

        featureShift = (
            ((dfXValidation.mean() - dfXTrain.mean()) / dfXTrain.std())
            .abs()
            .sort_values(ascending=False)
        )

        print("\n==============================")
        print("LARGEST TRAIN-VALIDATION FEATURE SHIFTS")
        print("==============================")
        print(featureShift.head(15))
        print("==============================\n")

        modelTrainer = ModelTrainer(modelType="logistic")

        modelTrainer.train(dfXTrain, dfYTrain)

        coefficients = modelTrainer.getCoefficients(dfXTrain.columns)

        print("\n==============================")
        print("MODEL COEFFICIENTS")
        print("==============================")
        print(coefficients)
        print("==============================\n")

        predictions = modelTrainer.predict(dfXValidation)
        probabilities = modelTrainer.predictProbabilities(dfXValidation)

        trainPredictions = modelTrainer.predict(dfXTrain)

        trainProbabilities = modelTrainer.predictProbabilities(dfXTrain)

        print("\n==============================")
        print("ML TRAINING RESULTS")
        print("==============================")

        print("Accuracy:", accuracy_score(dfYTrain, trainPredictions))

        print("Precision:", precision_score(dfYTrain, trainPredictions))

        print("Recall:", recall_score(dfYTrain, trainPredictions))

        print("ROC AUC:", roc_auc_score(dfYTrain, trainProbabilities))

        print("Balanced accuracy:", balanced_accuracy_score(dfYTrain, trainPredictions))

        print("Positive rate:", dfYTrain.mean())

        print("Predicted positive rate:", trainPredictions.mean())

        print("==============================")

        accuracy = accuracy_score(dfYValidation, predictions)

        precision = precision_score(dfYValidation, predictions)

        recall = recall_score(dfYValidation, predictions)

        auc = roc_auc_score(dfYValidation, probabilities)

        matrix = confusion_matrix(dfYValidation, predictions)

        print("\n==============================")
        print("ML VALIDATION RESULTS")
        print("==============================")

        print("Accuracy:", accuracy)
        print("Precision:", precision)
        print("Recall:", recall)
        print("ROC AUC:", auc)

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

        print("==============================\n")

        return modelTrainer, optimizedParams

    def splitData(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

        trainSplit = int(len(df) * 0.6)
        validationSplit = int(len(df) * 0.8)

        dfTrain = df.iloc[:trainSplit]
        dfValidation = df.iloc[trainSplit:validationSplit]
        dfTest = df.iloc[validationSplit:]

        return dfTrain, dfValidation, dfTest
