from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class ModelTrainer:
    
    def __init__(self):
        
        self.scaler = StandardScaler()
        self.model = LogisticRegression(max_iter = 2000)
        
    def train(self, X_train, y_train):
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        self.model.fit(X_train_scaled, y_train)
        
    def predict(self, X):
        
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict(X_scaled)
    
    def predictProbabilities(self, X):
        
        X_scaled = self.scaler.transform(X)
        
        return self.model.predict_proba(X_scaled)[:, 1]