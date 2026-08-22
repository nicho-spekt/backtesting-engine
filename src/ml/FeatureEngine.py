import pandas as pd

class FeatureEngine:
    
    def run(self, df: pd.DataFrame, optimizedParams, interval):
        
        dfFeatures = df.copy().sort_index()
        
        dfFeatures["Return_1"] = dfFeatures["Close"].pct_change()

        dfFeatures["Return_5"] = (dfFeatures["Close"].pct_change(5))

        dfFeatures["Return_20"] = (dfFeatures["Close"].pct_change(20))

        dfFeatures["Volatility_20"] = (dfFeatures["Return_1"].rolling(20).std())
        
        for strategyClass, params in optimizedParams.items():
            
            strategy = strategyClass(**params)
            strategyFeatures = strategy.generateFeature(df)
            
            dfFeatures = dfFeatures.join(strategyFeatures, how = 'inner')
            
        dfFeatures["Target"] = (dfFeatures["Close"].shift(-1) > dfFeatures["Close"]).astype(int)
        dfFeatures.dropna(inplace=True)
        
        return dfFeatures
            