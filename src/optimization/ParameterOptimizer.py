from optimization.StrategySearchSpaces import STRATEGY_SEARCH_SPACES
from itertools import product
import metrics_cpp
from analytics.MetricsCalculator import MetricsCalculator

class ParameterOptimizer:
    
    def optimizeStrategy(self, strategyClass, df, backtester, interval):
        
        paramCombinations = self.generateCombinations(strategyClass, interval)
        bestScore = float("-inf")
        bestParams = None
        
        for combination in paramCombinations:
            
            strategy = strategyClass(**combination)
            dfSignals = strategy.generateSignals(df)
            dfBacktested = backtester.run(dfSignals, strategy.execution_delay)
            returns = dfBacktested["Portfolio_return_period"].astype(float).tolist()
            portfolio_values = dfBacktested["Total_value"].astype(float).tolist()
            dfMetrics = metrics_cpp.calculateAll(returns, portfolio_values, MetricsCalculator.PERIODS_PER_YEAR[interval])
            
            if dfMetrics.sharpe_ratio > bestScore:
                bestScore = dfMetrics.sharpe_ratio
                bestParams = combination
            
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
            