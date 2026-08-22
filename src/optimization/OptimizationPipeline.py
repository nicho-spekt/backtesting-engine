from optimization.ParameterOptimizer import ParameterOptimizer
from analytics.MetricsCalculator import MetricsCalculator

class OptimizationPipeline:
    
    def run(self, strategyClass, df, backtester, interval):
        
        optimizer = ParameterOptimizer()
        calculator = MetricsCalculator()
        
        splitIndex = int(len(df) * 0.85)
        
        optimizationDf = df.iloc[:splitIndex]
        testDf = df.iloc[splitIndex:]

        bestScore, bestParams = optimizer.optimizeStrategy(strategyClass, optimizationDf, backtester, interval)
        
        print("==============================")
        print("Optimization best Sharpe:", bestScore)
        print("Optimization best parameters:", bestParams)
        print("==============================\n")
        
        strategy = strategyClass(**bestParams)
        
        dfSignals = strategy.generateSignals(testDf)
        dfBacktested = backtester.run(dfSignals, strategy.execution_delay)

        testMetrics = calculator.calculateMetrics(dfBacktested, interval)
        
        print("==============================")
        print("Test sharpe:", testMetrics["Sharpe_ratio"].iloc[0])
        print("==============================\n")
        
        return bestScore, bestParams, testMetrics
        
        
        
        