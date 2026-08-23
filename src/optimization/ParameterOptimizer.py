from optimization.StrategySearchSpaces import STRATEGY_SEARCH_SPACES
from itertools import product
import metrics_cpp
from analytics.MetricsCalculator import MetricsCalculator
import math
import time

class ParameterOptimizer:
    
    def optimizeStrategy(self, strategyClass, df, backtester, interval = 1):
        
        paramCombinations = self.generateCombinations(strategyClass, interval)
        bestScore = float("-inf")
        bestParams = None
        
        signalTime = 0.0
        backtestTime = 0.0
        metricsTime = 0.0
        
        for combination in paramCombinations:
            
            start = time.perf_counter()
            strategy = strategyClass(**combination)
            dfSignals = strategy.generateSignals(df)
            signalTime += time.perf_counter() - start
            
            start = time.perf_counter()
            dfBacktested = backtester.run(dfSignals, strategy.execution_delay)
            backtestTime += time.perf_counter() - start
            
            returns = dfBacktested["Portfolio_return_period"].astype(float).tolist()
            portfolio_values = dfBacktested["Total_value"].astype(float).tolist()
            
            start = time.perf_counter()
            dfMetrics = metrics_cpp.calculateAll(returns, portfolio_values, MetricsCalculator.PERIODS_PER_YEAR[interval])
            metricsTime += time.perf_counter() - start
            
            sharpeScore = dfMetrics.sharpe_ratio
            
            if not math.isfinite(sharpeScore):
                continue
            
            if dfMetrics.sharpe_ratio > bestScore:
                bestScore = dfMetrics.sharpe_ratio
                bestParams = combination
        
        print(f"Signal time: {signalTime}")
        print(f"Backtest time: {backtestTime}")
        print(f"Metrics time: {metricsTime}")
            
        return bestScore, bestParams
    
    def generateCombinations(self, strategyClass, interval):
        
        specs = STRATEGY_SEARCH_SPACES[strategyClass][interval]
        paramValues = {}
        
        for param, value in specs.items():
            paramValues[param] = self.getParameterValues(value)
        
        paramCombinations = product(*paramValues.values())
        
        parameterNames = paramValues.keys()

        for combination in paramCombinations:
            params = dict(zip(parameterNames, combination))
            
            if strategyClass.validateParameters(params):
                yield params
            
    
    def getParameterValues(self, parameterSpec):
        
        paramValues = []
        index = parameterSpec.minimum
        
        while index <= parameterSpec.maximum:
            
            paramValues.append(parameterSpec.parameter_type(index))
            index += parameterSpec.step
            
        return paramValues
            