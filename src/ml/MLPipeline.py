import pandas as pd
from optimization.ParameterOptimizer import ParameterOptimizer
from ml.FeatureEngine import FeatureEngine
from ml.ModelTrainer import ModelTrainer

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    confusion_matrix,
    roc_auc_score
)

class MLPipeline:
    
    def run(self, df: pd.DataFrame, backtester, interval = 1):
        
        dfTrain, dfValidation, dfTest = self.splitData(df)
        
        optimizer = ParameterOptimizer()
        optimizedParams = optimizer.optimizeAllStrategies(dfTrain, backtester, interval)
        
        featureEngine = FeatureEngine()
        dfTrainFeatures = featureEngine.run(dfTrain, optimizedParams, interval)
        dfValidationFeatures = featureEngine.run(dfValidation, optimizedParams, interval)
        
        dfXTrain = dfTrainFeatures.drop(columns=["Open", "High", "Low", "Close", "Volume", "Target"])
        dfYTrain = dfTrainFeatures["Target"].astype(int)
        
        dfXValidation = dfValidationFeatures.drop(columns=["Open", "High", "Low", "Close", "Volume", "Target"])
        dfYValidation = dfValidationFeatures["Target"].astype(int)
        
        modelTrainer = ModelTrainer()
        
        modelTrainer.train(dfXTrain, dfYTrain)
        predictions = modelTrainer.predict(dfXValidation)
        probabilities = modelTrainer.predictProbabilities(dfXValidation)
        
        accuracy = accuracy_score(
            dfYValidation,
            predictions
        )

        precision = precision_score(
            dfYValidation,
            predictions
        )

        recall = recall_score(
            dfYValidation,
            predictions
        )

        auc = roc_auc_score(
            dfYValidation,
            probabilities
        )

        matrix = confusion_matrix(
            dfYValidation,
            predictions
        )
        
        print("\n==============================")
        print("ML VALIDATION RESULTS")
        print("==============================")

        print("Accuracy:", accuracy)
        print("Precision:", precision)
        print("Recall:", recall)
        print("ROC AUC:", auc)

        print("\nConfusion Matrix:")
        print(matrix)

        print("==============================\n")

        return modelTrainer, optimizedParams

    def splitData(self, df: pd.DataFrame) -> pd.DataFrame:
        
        trainSplit = int(len(df) * 0.6)
        validationSplit = int(len(df) * 0.8)
        
        dfTrain = df.iloc[:trainSplit]
        dfValidation = df.iloc[trainSplit:validationSplit]
        dfTest = df.iloc[validationSplit:]
        
        return dfTrain, dfValidation, dfTest
        