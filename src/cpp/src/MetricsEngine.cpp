#include "MetricsEngine.h"
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <numeric>

double MetricsEngine::getCumulativeReturn(const std::vector<double>& portfolioValues) {
    if(portfolioValues.empty()) {
        throw std::invalid_argument("Portfolio values vector is empty.");
    }

    double starting_value = portfolioValues.front();
    double ending_value = portfolioValues.back();
    return (ending_value / starting_value) - 1.0 * 100.0;
}

double MetricsEngine::getPeriodVolatility(const std::vector<double>& returns) {
    if(returns.empty()) {
        throw std::invalid_argument("Returns vector is empty.");
    }

    double mean = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
    double sum_squared_diffs = std::accumulate(returns.begin(), returns.end(), 0.0, [mean](double sum, double x) {
        return sum + (x - mean) * (x - mean);
    });

    double variance = sum_squared_diffs / (returns.size() - 1);
    return std::sqrt(variance);
}