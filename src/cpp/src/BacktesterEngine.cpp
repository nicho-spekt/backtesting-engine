#include <BacktesterEngine.h>
#include <stdexcept>

BacktesterEngine::BacktestResult BacktesterEngine::run(const std::vector<double> &prices, const std::vector<int> &trades, double initialCapital, double commission, double slippage)
{

    if (prices.size() != trades.size())
    {
        throw std::invalid_argument("Prices and trades must have the same size.");
    }

    double cash{initialCapital};
    int shares{0};

    BacktestResult results{};

    results.shares.reserve(prices.size());
    results.cash.reserve(prices.size());
    results.positionValues.reserve(prices.size());
    results.totalValues.reserve(prices.size());
    results.portfolioReturns.reserve(prices.size());
    results.portfolioReturnPeriod.reserve(prices.size());

    for (auto i = std::size_t{0}; i < prices.size(); ++i)
    {

        int tradeSignal{trades[i]};
        double tradePrice = {prices[i]};

        if (tradeSignal == 1)
        {

            double executionPrice{tradePrice * (1 + slippage)};
            int sharesToBuy{static_cast<int>((cash - commission) / executionPrice)};

            if (sharesToBuy > 0)
            {

                cash -= sharesToBuy * executionPrice + commission;
                shares += sharesToBuy;
            }
        }
        else if (tradeSignal == -1)
        {

            double executionPrice{tradePrice * (1.0 - slippage)};
            cash += shares * executionPrice - commission;
            shares = 0;
        }

        double positionValue{shares * tradePrice};
        double totalValue{positionValue + cash};
        double portfolioReturnPeriod{0.0};

        if (i > 0)
        {
            portfolioReturnPeriod = {(totalValue / results.totalValues[i - 1] - 1.0)};
        }

        results.shares.push_back(shares);
        results.cash.push_back(cash);
        results.positionValues.push_back(positionValue);
        results.totalValues.push_back(totalValue);
        results.portfolioReturns.push_back((totalValue / initialCapital - 1) * 100.0);
        results.portfolioReturnPeriod.push_back(portfolioReturnPeriod);
    }

    return results;
}