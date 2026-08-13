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

double MetricsEngine::getAnnualizedVolatility(const std::vector<double>& returns, int periodsPerYear) {
    double period_volatility = getPeriodVolatility(returns);
    if(!period_volatility) {
        throw std::invalid_argument("Returns vector is empty.");
    }
    if(periodsPerYear <= 0) {
        throw std::invalid_argument("Periods per year must be positive.");
    }
    return period_volatility * std::sqrt(periodsPerYear);
}

double MetricsEngine::getSharpeRatio(const std::vector<double>& returns, int periodsPerYear) {
    double mean = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
    double std_dev = getPeriodVolatility(returns);

    if(std_dev == 0) {
        throw std::invalid_argument("Standard deviation is zero.");
    }


    return mean / std_dev * std::sqrt(periodsPerYear);
}

double MetricsEngine::getMaxDrawdown(const std::vector<double>& portfolioValues) {
    if(portfolioValues.empty()) {
        throw std::invalid_argument("Portfolio values vector is empty.");
    }

    double max_drawdown = 0.0;
    double peak = portfolioValues.front();

    for(const auto& value : portfolioValues) {
        if(value > peak) {
            peak = value;
        }
        double drawdown = (peak - value) / peak;
        if(drawdown > max_drawdown) {
            max_drawdown = drawdown;
        }
    }

    return max_drawdown * 100.0;
}

