import pandas as pd

class FeatureEngine:
    
    FEATURE_COLUMNS = [
    "Return_1",
    "Return_5",
    "Return_20",
    "Volatility_20",

    "Volume_change",
    "Volume_vs_avg20",
    "Intraday_range",
    "Gap",

    "Ma_spread_pct",
    "Ma_short_slope",
    "Ma_long_slope",
    "Ma_price_to_short",
    "Ma_price_to_long",
    "Ma_signal",

    "RSI_value",
    "RSI_centered",
    "RSI_change",
    "RSI_distance_lower",
    "RSI_distance_upper",
    "RSI_signal",

    "BB_percent_b",
    "BB_bandwidth",
    "BB_distance_middle",
    "BB_bandwidth_change",
    "BB_signal",

    "Breakout_distance_high",
    "Breakout_distance_low",
    "Breakout_channel_width",
    "Breakout_strength",
    "Breakout_signal"
    ]
    
    def run(self, df: pd.DataFrame, optimizedParams, interval = 1):
        
        dfFeatures = df.copy().sort_index()
        
        dfFeatures["Return_1"] = dfFeatures["Close"].pct_change()

        dfFeatures["Return_5"] = (dfFeatures["Close"].pct_change(5))

        dfFeatures["Return_20"] = (dfFeatures["Close"].pct_change(20))

        dfFeatures["Volatility_20"] = (dfFeatures["Return_1"].rolling(20).std())
        
        dfFeatures["Volume_change"] = (dfFeatures["Volume"].pct_change())

        dfFeatures["Volume_vs_avg20"] = (dfFeatures["Volume"] / dfFeatures["Volume"].rolling(20).mean())
        
        dfFeatures["Intraday_range"] = ((dfFeatures["High"] - dfFeatures["Low"]) / dfFeatures["Close"])

        dfFeatures["Gap"] = (dfFeatures["Open"] / dfFeatures["Close"].shift(1) - 1.0)
        
        for strategyClass, params in optimizedParams.items():
            
            strategy = strategyClass(**params)
            strategyFeatures = strategy.generateFeatures(df)
            
            dfFeatures = dfFeatures.join(strategyFeatures, how = 'inner')
            
        nextClose = df["Close"].shift(-1)
        
        target = (nextClose > df["Close"]).astype("Int64")
        
        target[nextClose.isna()] = pd.NA
        
        dfFeatures["Target"] = target
        
        dfFeatures.dropna(inplace=True)
        
        return dfFeatures
            