from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd


class ModelTrainer:

    def __init__(self, modelType="logistic"):

        self.modelType = modelType
        self.scaler = None

        if modelType == "logistic":

            self.scaler = StandardScaler()

            self.model = LogisticRegression(
                max_iter=1000,
                C=0.1
            )

        elif modelType == "random_forest":

            self.model = RandomForestClassifier(
                n_estimators=300,
                max_depth=5,
                random_state=42,
                n_jobs=-1
            )

        else:
            raise ValueError(
                f"Unknown model type: {modelType}"
            )


    def train(self, X, y):

        if self.scaler is not None:
            X = self.scaler.fit_transform(X)

        self.model.fit(X, y)


    def predict(self, X):

        if self.scaler is not None:
            X = self.scaler.transform(X)

        return self.model.predict(X)


    def predictProbabilities(self, X):

        if self.scaler is not None:
            X = self.scaler.transform(X)

        return self.model.predict_proba(X)[:, 1]
    
    def getCoefficients(self, featureNames):

        if self.modelType != "logistic":
            raise ValueError("Coefficients are only available for Logistic Regression.")

        return pd.Series(self.model.coef_[0], index=featureNames).sort_values(key=abs, ascending=False)