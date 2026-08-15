from optimization.ParameterSpec import ParameterSpec

from strategies.MaCrossover import MaCrossover
from strategies.Rsi import Rsi
from strategies.BollingerBands import BollingerBands
from strategies.BreakoutMomentum import BreakoutMomentum


STRATEGY_SEARCH_SPACES = {

    MaCrossover: {

        "1d": {
            "crossover_first": ParameterSpec(
                minimum=5,
                maximum=50,
                step=5,
                parameter_type=int
            ),

            "crossover_second": ParameterSpec(
                minimum=50,
                maximum=250,
                step=10,
                parameter_type=int
            ),
        },

        "1wk": {
            "crossover_first": ParameterSpec(
                minimum=2,
                maximum=12,
                step=2,
                parameter_type=int
            ),

            "crossover_second": ParameterSpec(
                minimum=12,
                maximum=52,
                step=4,
                parameter_type=int
            ),
        },

        "1mo": {
            "crossover_first": ParameterSpec(
                minimum=2,
                maximum=6,
                step=1,
                parameter_type=int
            ),

            "crossover_second": ParameterSpec(
                minimum=6,
                maximum=24,
                step=3,
                parameter_type=int
            ),
        },
    },

    Rsi: {

        "1d": {
            "window": ParameterSpec(
                minimum=5,
                maximum=30,
                step=1,
                parameter_type=int
            ),

            "lower_std_threshold": ParameterSpec(
                minimum=15,
                maximum=40,
                step=5,
                parameter_type=int
            ),

            "upper_std_threshold": ParameterSpec(
                minimum=60,
                maximum=85,
                step=5,
                parameter_type=int
            ),
        },

        "1wk": {
            "window": ParameterSpec(
                minimum=2,
                maximum=12,
                step=1,
                parameter_type=int
            ),

            "lower_std_threshold": ParameterSpec(
                minimum=15,
                maximum=40,
                step=5,
                parameter_type=int
            ),

            "upper_std_threshold": ParameterSpec(
                minimum=60,
                maximum=85,
                step=5,
                parameter_type=int
            ),
        },

        "1mo": {
            "window": ParameterSpec(
                minimum=2,
                maximum=8,
                step=1,
                parameter_type=int
            ),

            "lower_std_threshold": ParameterSpec(
                minimum=15,
                maximum=40,
                step=5,
                parameter_type=int
            ),

            "upper_std_threshold": ParameterSpec(
                minimum=60,
                maximum=85,
                step=5,
                parameter_type=int
            ),
        },
    },

    BollingerBands: {

        "1d": {
            "window": ParameterSpec(
                minimum=10,
                maximum=50,
                step=5,
                parameter_type=int
            ),

            "window_dev": ParameterSpec(
                minimum=1.0,
                maximum=3.0,
                step=0.25,
                parameter_type=float
            ),
        },

        "1wk": {
            "window": ParameterSpec(
                minimum=4,
                maximum=26,
                step=2,
                parameter_type=int
            ),

            "window_dev": ParameterSpec(
                minimum=1.0,
                maximum=3.0,
                step=0.25,
                parameter_type=float
            ),
        },

        "1mo": {
            "window": ParameterSpec(
                minimum=3,
                maximum=18,
                step=1,
                parameter_type=int
            ),

            "window_dev": ParameterSpec(
                minimum=1.0,
                maximum=3.0,
                step=0.25,
                parameter_type=float
            ),
        },
    },

    BreakoutMomentum: {

        "1d": {
            "window_high": ParameterSpec(
                minimum=20,
                maximum=100,
                step=10,
                parameter_type=int
            ),

            "window_low": ParameterSpec(
                minimum=5,
                maximum=50,
                step=5,
                parameter_type=int
            ),
        },

        "1wk": {
            "window_high": ParameterSpec(
                minimum=4,
                maximum=52,
                step=4,
                parameter_type=int
            ),

            "window_low": ParameterSpec(
                minimum=2,
                maximum=12,
                step=2,
                parameter_type=int
            ),
        },

        "1mo": {
            "window_high": ParameterSpec(
                minimum=3,
                maximum=18,
                step=3,
                parameter_type=int
            ),

            "window_low": ParameterSpec(
                minimum=2,
                maximum=9,
                step=1,
                parameter_type=int
            ),
        },
    },
}