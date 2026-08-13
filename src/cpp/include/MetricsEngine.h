#pragma once
#include <vector>

class MetricsEngine{

    public: 
    double getCumulativeReturn(const std::vector<double>& portfolioValues); 
    double getPeriodVolatility(const std::vector<double>& returns);
    double getAnnualizedVolatility(const std::vector<double>& returns, int periodsPerYear);
    double getShapreRatio(const std::vector<double>& returns, int periodsPerYear);
    double getMaxDrawdown(const std::vector<double>& portfolioValues);

};