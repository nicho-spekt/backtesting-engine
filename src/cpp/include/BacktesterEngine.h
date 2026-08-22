#pragma once
#include <vector>
#ifndef BACKTESTERENGINE_H
#define BACKTESTERENGINE_H

class BacktesterEngine
{

public:
    struct BacktestResult
    {

        std::vector<int> shares;
        std::vector<double> cash;
        std::vector<double> positionValues;
        std::vector<double> totalValues;
        std::vector<double> portfolioReturns;
        std::vector<double> portfolioReturnPeriod;
    };

    static BacktestResult run(const std::vector<double> &prices, const std::vector<int> &trades, double initialCapital, double commission, double slippage);
};

#endif