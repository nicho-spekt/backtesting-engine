#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "MetricsEngine.h"

namespace py = pybind11;

PYBIND11_MODULE(metrics_cpp, m)
{
    m.doc() = "C++ metrics engine for the backtesting project";

    py::class_<MetricsEngine::MetricsResult>(
        m,
        "MetricsResult")
        .def_readonly(
            "cumulative_return",
            &MetricsEngine::MetricsResult::cumulativeReturn)
        .def_readonly(
            "period_volatility",
            &MetricsEngine::MetricsResult::periodVolatility)
        .def_readonly(
            "annualized_volatility",
            &MetricsEngine::MetricsResult::annualizedVolatility)
        .def_readonly(
            "sharpe_ratio",
            &MetricsEngine::MetricsResult::sharpeRatio)
        .def_readonly(
            "max_drawdown",
            &MetricsEngine::MetricsResult::maxDrawdown);

    m.def(
        "calculateAll",
        &MetricsEngine::calculateAll,
        py::arg("returns"),
        py::arg("portfolio_values"),
        py::arg("periods_per_year"));

    m.def(
        "cumulative_return",
        &MetricsEngine::getCumulativeReturn,
        py::arg("portfolio_values"));

    m.def(
        "period_volatility",
        &MetricsEngine::getPeriodVolatility,
        py::arg("returns"));

    m.def(
        "annualized_volatility",
        &MetricsEngine::getAnnualizedVolatility,
        py::arg("returns"),
        py::arg("periods_per_year"));

    m.def(
        "sharpe_ratio",
        &MetricsEngine::getSharpeRatio,
        py::arg("returns"),
        py::arg("periods_per_year"));

    m.def(
        "max_drawdown",
        &MetricsEngine::getMaxDrawdown,
        py::arg("portfolio_values"));
}