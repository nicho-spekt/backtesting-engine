import pandas as pd
from optimization import ParameterOptimizer
import numpy as np
from strategies.Atr import Atr


class FeatureEngine:

    FEATURE_COLUMNS = [
        "Return_1",
        "Return_2",
        "Return_3",
        "Return_5",
        "Return_10",
        "Return_20",
        "Return_60",
        "Momentum_5_20",
        "Momentum_20_60",
        "Volatility_5",
        "Volatility_10",
        "Volatility_20",
        "Volatility_60",
        "Volatility_ratio_5_20",
        "Volatility_ratio_20_60",
        "Volume_change",
        "Volume_vs_avg20",
        "Volume_z20",
        "Dollar_volume_z20",
        "Intraday_range",
        "Gap",
        "Range_position_20",
        "Range_position_60",
        "Stochastic_K",
        "Stochastic_D",
        "Ma_spread_pct",
        "Ma_short_slope",
        "Ma_long_slope",
        "Ma_price_to_short",
        "Ma_price_to_long",
        "Ma_signal",
        "RSI_value",
        "RSI_change",
        "RSI_signal",
        "BB_percent_b",
        "BB_bandwidth",
        "BB_distance_middle",
        "BB_bandwidth_change",
        "BB_signal",
        "Breakout_distance_high",
        "Breakout_distance_low",
        "Breakout_channel_width",
        "Breakout_signal",
        "MACD_pct",
        "MACD_signal_pct",
        "MACD_histogram_pct",
        "MACD_signal",
        "ATR_pct",
        "ATR_change",
        "ATR_ratio",
    ]

    LAG_COLUMNS = [
        "RSI_value",
        "RSI_change",
        "BB_percent_b",
        "BB_bandwidth",
        "Ma_spread_pct",
        "Breakout_distance_high",
        "Volatility_20",
        "Volume_vs_avg20",
    ]

    @classmethod
    def getFeatureColumns(cls):

        columns = cls.FEATURE_COLUMNS.copy()

        for column in cls.LAG_COLUMNS:
            for lag in [1, 2, 3, 5]:
                columns.append(f"{column}_lag_{lag}")

        return columns

    def run(self, df: pd.DataFrame, optimizedParams, interval="1d", predictionHorizon=1):

        dfFeatures = df.copy().sort_index()

        dfFeatures["Return_1"] = dfFeatures["Close"].pct_change()

        dfFeatures["Return_5"] = dfFeatures["Close"].pct_change(5)

        dfFeatures["Return_20"] = dfFeatures["Close"].pct_change(20)

        dfFeatures["Volatility_20"] = dfFeatures["Return_1"].rolling(20).std()

        dfFeatures["Volume_change"] = dfFeatures["Volume"].pct_change()

        dfFeatures["Volume_vs_avg20"] = (
            dfFeatures["Volume"] / dfFeatures["Volume"].rolling(20).mean()
        )

        dfFeatures["Intraday_range"] = (
            dfFeatures["High"] - dfFeatures["Low"]
        ) / dfFeatures["Close"]

        dfFeatures["Gap"] = dfFeatures["Open"] / dfFeatures["Close"].shift(1) - 1.0

        for strategyClass, params in optimizedParams.items():

            strategy = strategyClass(**params)
            strategyFeatures = strategy.generateFeatures(df)

            dfFeatures = dfFeatures.join(strategyFeatures, how="inner")

        atr = Atr(window=14)

        atrFeatures = atr.generateFeatures(df)

        dfFeatures = dfFeatures.join(atrFeatures, how="inner")

        for column in self.LAG_COLUMNS:
            for lag in [1, 2, 3, 5]:
                dfFeatures[f"{column}_lag_{lag}"] = dfFeatures[column].shift(lag)

        nextClose = df["Close"].shift(-predictionHorizon)

        for window in [2, 3, 5, 10, 20, 60]:
            dfFeatures[f"Return_{window}"] = dfFeatures["Close"].pct_change(window)

        dfFeatures["Momentum_5_20"] = dfFeatures["Return_5"] - dfFeatures["Return_20"]

        dfFeatures["Momentum_20_60"] = dfFeatures["Return_20"] - dfFeatures["Return_60"]

        returns = dfFeatures["Close"].pct_change()

        dfFeatures["Volatility_5"] = returns.rolling(5).std()

        dfFeatures["Volatility_10"] = returns.rolling(10).std()

        dfFeatures["Volatility_20"] = returns.rolling(20).std()

        dfFeatures["Volatility_60"] = returns.rolling(60).std()

        dfFeatures["Volatility_ratio_5_20"] = (
            dfFeatures["Volatility_5"] / dfFeatures["Volatility_20"]
        )

        dfFeatures["Volatility_ratio_20_60"] = (
            dfFeatures["Volatility_20"] / dfFeatures["Volatility_60"]
        )

        high20 = dfFeatures["High"].rolling(20).max()

        low20 = dfFeatures["Low"].rolling(20).min()

        dfFeatures["Range_position_20"] = (dfFeatures["Close"] - low20) / (
            high20 - low20
        )

        high60 = dfFeatures["High"].rolling(60).max()
        low60 = dfFeatures["Low"].rolling(60).min()

        dfFeatures["Range_position_60"] = (dfFeatures["Close"] - low60) / (
            high60 - low60
        )

        low14 = dfFeatures["Low"].rolling(14).min()
        high14 = dfFeatures["High"].rolling(14).max()

        dfFeatures["Stochastic_K"] = (
            100 * (dfFeatures["Close"] - low14) / (high14 - low14)
        )

        dfFeatures["Stochastic_D"] = dfFeatures["Stochastic_K"].rolling(3).mean()

        dollarVolume = dfFeatures["Close"] * dfFeatures["Volume"]

        logDollarVolume = np.log1p(dollarVolume)

        dfFeatures["Dollar_volume_z20"] = (
            logDollarVolume - logDollarVolume.rolling(20).mean()
        ) / logDollarVolume.rolling(20).std()

        dfFeatures["Volume_z20"] = (
            dfFeatures["Volume"] - dfFeatures["Volume"].rolling(20).mean()
        ) / dfFeatures["Volume"].rolling(20).std()

        target = (nextClose > df["Close"]).astype("Int64")

        target[nextClose.isna()] = pd.NA

        dfFeatures["Target"] = target

        dfFeatures.replace([np.inf, -np.inf], np.nan, inplace=True)

        dfFeatures.dropna(inplace=True)

        return dfFeatures
