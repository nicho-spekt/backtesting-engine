#pragma once
#include <vector>
#ifndef METRICSENGINE_H
#define METRICSENGINE_H

class MetricsEngine
{

public:
    struct MetricsResult
    {

        double cumulativeReturn;
        double periodVolatility;
        double annualizedVolatility;
        double sharpeRatio;
        double maxDrawdown;
    };

    static double getCumulativeReturn(const std::vector<double> &portfolioValues);
    static double getPeriodVolatility(const std::vector<double> &returns);
    static double getAnnualizedVolatility(const std::vector<double> &returns, int periodsPerYear);
    static double getSharpeRatio(const std::vector<double> &returns, int periodsPerYear);
    static double getMaxDrawdown(const std::vector<double> &portfolioValues);

    static MetricsResult calculateAll(const std::vector<double> &returns, const std::vector<double> &portfolioValues, int periodsPerYear);
};

#endif