import sys
from datetime import date
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from data.DataLoader import DataLoader
from engine.Backtester import Backtester
from analystics.MetricsCalculator import MetricsCalculator

from strategies.BuyHold import BuyHold
from strategies.MaCrossover import MaCrossover
from strategies.Rsi import Rsi
from strategies.BollingerBands import BollingerBands
from strategies.BreakoutMomentum import BreakoutMomentum


class BacktestingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.portfolio_df = None
        self.metrics_df = None

        self.setWindowTitle("Quantitative Backtesting Engine")
        self.resize(1250, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # -------------------------------------------------
        # LEFT PANEL - configuration
        # -------------------------------------------------
        controls = QFrame()
        controls.setMaximumWidth(360)
        controls_layout = QVBoxLayout(controls)

        title = QLabel("Backtest Configuration")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        controls_layout.addWidget(title)

        general_box = QGroupBox("Market Data")
        general_form = QFormLayout(general_box)

        self.ticker_input = QLineEdit("VGT")
        self.ticker_input.setPlaceholderText("e.g. VGT, AAPL, SPY")
        general_form.addRow("Ticker:", self.ticker_input)

        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.start_date_input.setDate(QDate(2015, 1, 1))
        general_form.addRow("Start date:", self.start_date_input)

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        today = date.today()
        self.end_date_input.setDate(QDate(today.year, today.month, today.day))
        general_form.addRow("End date:", self.end_date_input)

        self.interval_input = QComboBox()
        self.interval_input.addItems(["1d", "1wk", "1mo"])
        general_form.addRow("Interval:", self.interval_input)

        self.capital_input = QDoubleSpinBox()
        self.capital_input.setRange(1_000, 1_000_000_000)
        self.capital_input.setDecimals(2)
        self.capital_input.setSingleStep(10_000)
        self.capital_input.setValue(100_000)
        self.capital_input.setPrefix("$")
        self.capital_input.setGroupSeparatorShown(True)
        general_form.addRow("Initial capital:", self.capital_input)

        controls_layout.addWidget(general_box)

        # -------------------------------------------------
        # Strategy selection
        # -------------------------------------------------
        strategy_box = QGroupBox("Strategy")
        strategy_layout = QVBoxLayout(strategy_box)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(
            [
                "Buy & Hold",
                "MA Crossover",
                "RSI",
                "Bollinger Bands",
                "Breakout Momentum",
            ]
        )
        strategy_layout.addWidget(self.strategy_combo)

        self.strategy_parameters = QStackedWidget()
        strategy_layout.addWidget(self.strategy_parameters)

        self._build_strategy_parameter_pages()

        self.strategy_combo.currentIndexChanged.connect(
            self.strategy_parameters.setCurrentIndex
        )

        controls_layout.addWidget(strategy_box)

        self.run_button = QPushButton("Run Backtest")
        self.run_button.setMinimumHeight(42)
        self.run_button.clicked.connect(self.run_backtest)
        controls_layout.addWidget(self.run_button)

        self.export_button = QPushButton("Export Results")
        self.export_button.setMinimumHeight(36)
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_results)
        controls_layout.addWidget(self.export_button)

        controls_layout.addStretch()

        main_layout.addWidget(controls)

        # -------------------------------------------------
        # RIGHT PANEL - results
        # -------------------------------------------------
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)

        results_title = QLabel("Results")
        results_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        results_layout.addWidget(results_title)

        self.summary_label = QLabel(
            "Choose a ticker, date range and strategy, then run a backtest."
        )
        self.summary_label.setWordWrap(True)
        results_layout.addWidget(self.summary_label)

        metrics_box = QGroupBox("Performance Summary")
        metrics_grid = QGridLayout(metrics_box)

        self.ending_value_label = self._create_metric_label("Ending Value")
        self.return_label = self._create_metric_label("Cumulative Return")
        self.sharpe_label = self._create_metric_label("Sharpe Ratio")
        self.drawdown_label = self._create_metric_label("Max Drawdown")

        metrics_grid.addWidget(self.ending_value_label, 0, 0)
        metrics_grid.addWidget(self.return_label, 0, 1)
        metrics_grid.addWidget(self.sharpe_label, 0, 2)
        metrics_grid.addWidget(self.drawdown_label, 0, 3)

        results_layout.addWidget(metrics_box)

        self.tabs = QTabWidget()

        # Portfolio tab
        portfolio_tab = QWidget()
        portfolio_layout = QVBoxLayout(portfolio_tab)

        self.portfolio_figure = Figure(figsize=(10, 5))
        self.portfolio_canvas = FigureCanvas(self.portfolio_figure)
        portfolio_layout.addWidget(self.portfolio_canvas)

        self.tabs.addTab(portfolio_tab, "Portfolio")

        # Signals tab
        signals_tab = QWidget()
        signals_layout = QVBoxLayout(signals_tab)

        self.signals_figure = Figure(figsize=(10, 5))
        self.signals_canvas = FigureCanvas(self.signals_figure)
        signals_layout.addWidget(self.signals_canvas)

        self.tabs.addTab(signals_tab, "Signals")

        # Trades tab
        trades_tab = QWidget()
        trades_layout = QVBoxLayout(trades_tab)

        self.trades_table = QTableWidget()
        self.trades_table.setAlternatingRowColors(True)
        self.trades_table.setSortingEnabled(False)
        trades_layout.addWidget(self.trades_table)

        self.tabs.addTab(trades_tab, "Trades")

        # Metrics tab
        metrics_tab = QWidget()
        metrics_layout = QVBoxLayout(metrics_tab)

        self.metrics_table = QTableWidget()
        self.metrics_table.setAlternatingRowColors(True)
        metrics_layout.addWidget(self.metrics_table)

        self.tabs.addTab(metrics_tab, "Metrics")

        results_layout.addWidget(self.tabs)

        main_layout.addWidget(results_widget, 1)

    # =====================================================
    # Strategy parameter widgets
    # =====================================================

    def _build_strategy_parameter_pages(self):
        # Buy & Hold
        buy_hold_page = QWidget()
        buy_hold_layout = QVBoxLayout(buy_hold_page)
        buy_hold_layout.addWidget(QLabel("No additional parameters."))
        buy_hold_layout.addStretch()
        self.strategy_parameters.addWidget(buy_hold_page)

        # MA Crossover
        ma_page = QWidget()
        ma_form = QFormLayout(ma_page)

        self.ma_short_input = QSpinBox()
        self.ma_short_input.setRange(1, 1000)
        self.ma_short_input.setValue(20)

        self.ma_long_input = QSpinBox()
        self.ma_long_input.setRange(2, 2000)
        self.ma_long_input.setValue(50)

        ma_form.addRow("Short window:", self.ma_short_input)
        ma_form.addRow("Long window:", self.ma_long_input)

        self.strategy_parameters.addWidget(ma_page)

        # RSI
        rsi_page = QWidget()
        rsi_form = QFormLayout(rsi_page)

        self.rsi_window_input = QSpinBox()
        self.rsi_window_input.setRange(2, 500)
        self.rsi_window_input.setValue(14)

        self.rsi_lower_input = QDoubleSpinBox()
        self.rsi_lower_input.setRange(0, 100)
        self.rsi_lower_input.setValue(30)

        self.rsi_upper_input = QDoubleSpinBox()
        self.rsi_upper_input.setRange(0, 100)
        self.rsi_upper_input.setValue(70)

        rsi_form.addRow("RSI window:", self.rsi_window_input)
        rsi_form.addRow("Buy threshold:", self.rsi_lower_input)
        rsi_form.addRow("Sell threshold:", self.rsi_upper_input)

        self.strategy_parameters.addWidget(rsi_page)

        # Bollinger Bands
        bb_page = QWidget()
        bb_form = QFormLayout(bb_page)

        self.bb_window_input = QSpinBox()
        self.bb_window_input.setRange(2, 1000)
        self.bb_window_input.setValue(20)

        self.bb_deviation_input = QDoubleSpinBox()
        self.bb_deviation_input.setRange(0.1, 10.0)
        self.bb_deviation_input.setDecimals(2)
        self.bb_deviation_input.setSingleStep(0.1)
        self.bb_deviation_input.setValue(2.0)

        bb_form.addRow("Window:", self.bb_window_input)
        bb_form.addRow("Std. deviation:", self.bb_deviation_input)

        self.strategy_parameters.addWidget(bb_page)

        # Breakout Momentum
        breakout_page = QWidget()
        breakout_form = QFormLayout(breakout_page)

        self.breakout_high_input = QSpinBox()
        self.breakout_high_input.setRange(2, 2000)
        self.breakout_high_input.setValue(50)

        self.breakout_low_input = QSpinBox()
        self.breakout_low_input.setRange(2, 2000)
        self.breakout_low_input.setValue(20)

        breakout_form.addRow("Breakout high window:", self.breakout_high_input)
        breakout_form.addRow("Exit low window:", self.breakout_low_input)

        self.strategy_parameters.addWidget(breakout_page)

    # =====================================================
    # Backtest flow
    # =====================================================

    def run_backtest(self):
        try:
            ticker = self.ticker_input.text().strip().upper()

            if not ticker:
                raise ValueError("Please enter a ticker.")

            start_date = self.start_date_input.date().toPython()
            end_date = self.end_date_input.date().toPython()

            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")

            interval = self.interval_input.currentText()
            initial_capital = self.capital_input.value()

            strategy = self._create_selected_strategy()

            self.run_button.setEnabled(False)
            self.run_button.setText("Running...")
            QApplication.setOverrideCursor(Qt.WaitCursor)
            QApplication.processEvents()

            loader = DataLoader(
                ticker,
                start_date.isoformat(),
                end_date.isoformat(),
            )

            market_df = loader.loadData(interval)

            strategy_df = strategy.generateSignals(market_df)

            if strategy_df.empty:
                raise ValueError(
                    "Not enough data for the selected strategy and timeframe."
                )

            backtester = Backtester(initial_capital)
            portfolio_df = backtester.run(strategy_df)

            calculator = MetricsCalculator()
            metrics_df = calculator.calculate_metric(portfolio_df)

            self.portfolio_df = portfolio_df
            self.metrics_df = metrics_df

            self._update_results(
                ticker=ticker,
                strategy_name=self.strategy_combo.currentText(),
                start_date=start_date,
                end_date=end_date,
            )

            self.export_button.setEnabled(True)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Backtest Error",
                str(error),
            )

        finally:
            QApplication.restoreOverrideCursor()
            self.run_button.setEnabled(True)
            self.run_button.setText("Run Backtest")

    def _create_selected_strategy(self):
        strategy_name = self.strategy_combo.currentText()

        if strategy_name == "Buy & Hold":
            return BuyHold()

        if strategy_name == "MA Crossover":
            short_window = self.ma_short_input.value()
            long_window = self.ma_long_input.value()

            if short_window >= long_window:
                raise ValueError(
                    "The short MA window must be smaller than the long MA window."
                )

            return MaCrossover(short_window, long_window)

        if strategy_name == "RSI":
            lower = self.rsi_lower_input.value()
            upper = self.rsi_upper_input.value()

            if lower >= upper:
                raise ValueError(
                    "The RSI buy threshold must be below the sell threshold."
                )

            return Rsi(
                self.rsi_window_input.value(),
                lower,
                upper,
            )

        if strategy_name == "Bollinger Bands":
            return BollingerBands(
                self.bb_window_input.value(),
                self.bb_deviation_input.value(),
            )

        if strategy_name == "Breakout Momentum":
            return BreakoutMomentum(
                self.breakout_high_input.value(),
                self.breakout_low_input.value(),
            )

        raise ValueError("Unknown strategy selected.")

    # =====================================================
    # Results display
    # =====================================================

    def _update_results(
        self,
        ticker,
        strategy_name,
        start_date,
        end_date,
    ):
        metrics = self.metrics_df.iloc[0]

        self.summary_label.setText(
            f"{ticker} | {strategy_name} | {start_date} to {end_date}"
        )

        self._set_metric(
            self.ending_value_label,
            "Ending Value",
            f"${metrics['Ending_value']:,.2f}",
        )

        self._set_metric(
            self.return_label,
            "Cumulative Return",
            f"{metrics['Cumulative_return%']:.2f}%",
        )

        self._set_metric(
            self.sharpe_label,
            "Sharpe Ratio",
            f"{metrics['Sharpe_ratio']:.3f}",
        )

        self._set_metric(
            self.drawdown_label,
            "Max Drawdown",
            f"{metrics['Max_drawdown%']:.2f}%",
        )

        self._plot_portfolio(ticker, strategy_name)
        self._plot_signals(ticker, strategy_name)
        self._populate_trades_table()
        self._populate_metrics_table()

    def _plot_portfolio(self, ticker, strategy_name):
        self.portfolio_figure.clear()
        ax = self.portfolio_figure.add_subplot(111)

        ax.plot(
            self.portfolio_df.index,
            self.portfolio_df["Total_value"],
            label="Portfolio Value",
        )

        ax.set_title(f"{ticker} - {strategy_name} Portfolio Value")
        ax.set_xlabel("Date")
        ax.set_ylabel("Portfolio Value ($)")
        ax.grid(True)
        ax.legend()

        self.portfolio_figure.tight_layout()
        self.portfolio_canvas.draw()

    def _plot_signals(self, ticker, strategy_name):
        self.signals_figure.clear()
        ax = self.signals_figure.add_subplot(111)

        ax.plot(
            self.portfolio_df.index,
            self.portfolio_df["Close"],
            label=ticker,
        )

        buys = self.portfolio_df[self.portfolio_df["Trade"] == 1]
        sells = self.portfolio_df[self.portfolio_df["Trade"] == -1]

        ax.scatter(
            buys.index,
            buys["Close"],
            marker="^",
            label="Buy",
        )

        ax.scatter(
            sells.index,
            sells["Close"],
            marker="v",
            label="Sell",
        )

        ax.set_title(f"{ticker} - {strategy_name} Signals")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.grid(True)
        ax.legend()

        self.signals_figure.tight_layout()
        self.signals_canvas.draw()

    def _populate_trades_table(self):
        trades_df = self.portfolio_df[
            self.portfolio_df["Trade"] != 0
        ].copy()

        wanted_columns = [
            "Close",
            "Signal",
            "Trade",
            "Shares",
            "Cash",
            "Total_value",
        ]

        columns = [
            column
            for column in wanted_columns
            if column in trades_df.columns
        ]

        self.trades_table.setSortingEnabled(False)
        self.trades_table.clear()
        self.trades_table.setColumnCount(len(columns) + 1)
        self.trades_table.setHorizontalHeaderLabels(["Date"] + columns)
        self.trades_table.setRowCount(len(trades_df))

        for row_number, (index, row) in enumerate(trades_df.iterrows()):
            self.trades_table.setItem(
                row_number,
                0,
                QTableWidgetItem(str(index)),
            )

            for column_number, column in enumerate(columns, start=1):
                value = row[column]

                if isinstance(value, float):
                    text = f"{value:,.4f}"
                else:
                    text = str(value)

                self.trades_table.setItem(
                    row_number,
                    column_number,
                    QTableWidgetItem(text),
                )

        self.trades_table.resizeColumnsToContents()
        self.trades_table.setSortingEnabled(True)

    def _populate_metrics_table(self):
        metrics = self.metrics_df.iloc[0]

        self.metrics_table.clear()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(
            ["Metric", "Value"]
        )
        self.metrics_table.setRowCount(len(metrics))

        for row_number, (name, value) in enumerate(metrics.items()):
            self.metrics_table.setItem(
                row_number,
                0,
                QTableWidgetItem(str(name)),
            )

            if isinstance(value, (float, int)):
                value_text = f"{value:,.4f}"
            else:
                value_text = str(value)

            self.metrics_table.setItem(
                row_number,
                1,
                QTableWidgetItem(value_text),
            )

        self.metrics_table.resizeColumnsToContents()

    # =====================================================
    # Export
    # =====================================================

    def export_results(self):
        if self.portfolio_df is None or self.metrics_df is None:
            return

        directory = QFileDialog.getExistingDirectory(
            self,
            "Choose Export Folder",
        )

        if not directory:
            return

        ticker = self.ticker_input.text().strip().upper()

        strategy_name = (
            self.strategy_combo.currentText()
            .lower()
            .replace(" ", "_")
            .replace("&", "and")
        )

        output_directory = Path(directory)

        portfolio_file = (
            output_directory
            / f"{ticker}_{strategy_name}_portfolio.csv"
        )

        metrics_file = (
            output_directory
            / f"{ticker}_{strategy_name}_metrics.csv"
        )

        self.portfolio_df.to_csv(portfolio_file)
        self.metrics_df.to_csv(metrics_file, index=False)

        QMessageBox.information(
            self,
            "Export Complete",
            f"Results saved to:\n{output_directory}",
        )

    # =====================================================
    # UI helpers
    # =====================================================

    @staticmethod
    def _create_metric_label(title):
        label = QLabel(f"{title}\n—")
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumHeight(75)
        label.setStyleSheet(
            """
            QLabel {
                border: 1px solid #999;
                border-radius: 6px;
                padding: 8px;
                font-size: 15px;
            }
            """
        )
        return label

    @staticmethod
    def _set_metric(label, title, value):
        label.setText(f"{title}\n{value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BacktestingApp()
    window.show()

    sys.exit(app.exec())