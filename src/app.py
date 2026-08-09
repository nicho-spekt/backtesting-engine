import sys
from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, Qt, QObject, QEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
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
from engine.ComparisonEngine import ComparisonEngine
from analystics.MetricsCalculator import MetricsCalculator

from strategies.BuyHold import BuyHold
from strategies.MaCrossover import MaCrossover
from strategies.Rsi import Rsi
from strategies.BollingerBands import BollingerBands
from strategies.BreakoutMomentum import BreakoutMomentum


class DisabledTabClickFilter(QObject):
    """Shows a message when the disabled Portfolio tab is clicked."""

    def __init__(self, app_window):
        super().__init__(app_window)
        self.app_window = app_window

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            tab_index = watched.tabAt(event.position().toPoint())

            if (
                tab_index == 0
                and self.app_window.mode_combo.currentText()
                == "Compare Strategies"
            ):
                QMessageBox.information(
                    self.app_window,
                    "Portfolio Tab Disabled",
                    "The Portfolio tab is disabled in Compare Strategies mode.\n\n"
                    "Use the Comparison tab to view all portfolio curves together, "
                    "or switch to Single Strategy mode to use the individual Portfolio tab."
                )
                return True

        return super().eventFilter(watched, event)


class BacktestingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.portfolio_df = None
        self.metrics_df = None
        self.portfolio_results = None
        self.comparison_df = None

        self.setWindowTitle("Quantitative Backtesting Engine")
        self.resize(1250, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

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
        
        today = QDate.currentDate()

        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.start_date_input.setDate(QDate(2015, 1, 1))
        self.start_date_input.setMaximumDate(today)
        general_form.addRow("Start date:", self.start_date_input)

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
 
        self.end_date_input.setDate(today)
        self.end_date_input.setMaximumDate(today)
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
        # Execution assumptions
        # -------------------------------------------------
        execution_box = QGroupBox("Execution Settings")
        execution_form = QFormLayout(execution_box)

        self.commission_input = QDoubleSpinBox()
        self.commission_input.setRange(0.0, 10_000.0)
        self.commission_input.setDecimals(2)
        self.commission_input.setSingleStep(0.50)
        self.commission_input.setValue(0.0)
        self.commission_input.setPrefix("$")
        self.commission_input.setToolTip(
            "Fixed commission charged for each executed buy or sell."
        )
        execution_form.addRow("Commission / trade:", self.commission_input)

        self.slippage_input = QDoubleSpinBox()
        self.slippage_input.setRange(0.0, 10.0)
        self.slippage_input.setDecimals(3)
        self.slippage_input.setSingleStep(0.01)
        self.slippage_input.setValue(0.0)
        self.slippage_input.setSuffix("%")
        self.slippage_input.setToolTip(
            "Simulated execution-price slippage. "
            "For example, 0.10% means 0.001 inside the Backtester."
        )
        execution_form.addRow("Slippage:", self.slippage_input)

        controls_layout.addWidget(execution_box)

        # -------------------------------------------------
        # Backtest mode
        # -------------------------------------------------
        mode_box = QGroupBox("Mode")
        mode_layout = QVBoxLayout(mode_box)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(
            [
                "Single Strategy",
                "Compare Strategies",
            ]
        )
        mode_layout.addWidget(self.mode_combo)
        controls_layout.addWidget(mode_box)

        # -------------------------------------------------
        # Single strategy selection
        # -------------------------------------------------
        self.strategy_box = QGroupBox("Strategy")
        strategy_layout = QVBoxLayout(self.strategy_box)

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

        # -------------------------------------------------
        # Comparison strategy selection
        # -------------------------------------------------
        self.comparison_box = QGroupBox("Strategies to Compare")
        comparison_layout = QVBoxLayout(self.comparison_box)

        self.compare_buy_hold = QCheckBox("Buy & Hold")
        self.compare_ma = QCheckBox("MA Crossover")
        self.compare_rsi = QCheckBox("RSI")
        self.compare_bollinger = QCheckBox("Bollinger Bands")
        self.compare_breakout = QCheckBox("Breakout Momentum")

        for checkbox in [
            self.compare_buy_hold,
            self.compare_ma,
            self.compare_rsi,
            self.compare_bollinger,
            self.compare_breakout,
        ]:
            checkbox.setChecked(True)
            comparison_layout.addWidget(checkbox)

        comparison_note = QLabel(
            "Check the strategies to include. Then use the Strategy "
            "Parameters section below to configure each selected strategy."
        )
        comparison_note.setWordWrap(True)
        comparison_layout.addWidget(comparison_note)

        self.comparison_box.setVisible(False)

        # In compare mode this appears ABOVE the parameter editor.
        controls_layout.addWidget(self.comparison_box)
        controls_layout.addWidget(self.strategy_box)

        self.mode_combo.currentTextChanged.connect(self._update_mode_ui)

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

        # In comparison mode, lets the user inspect one strategy's
        # Signals / Trades / Metrics while keeping the Comparison tab
        # for the multi-strategy portfolio view.
        self.detail_strategy_widget = QWidget()
        detail_strategy_layout = QHBoxLayout(self.detail_strategy_widget)
        detail_strategy_layout.setContentsMargins(0, 0, 0, 0)

        detail_strategy_label = QLabel("View strategy details:")
        self.detail_strategy_combo = QComboBox()

        detail_strategy_layout.addWidget(detail_strategy_label)
        detail_strategy_layout.addWidget(self.detail_strategy_combo, 1)

        self.detail_strategy_widget.setVisible(False)
        results_layout.addWidget(self.detail_strategy_widget)

        self.detail_strategy_combo.currentTextChanged.connect(
            self._update_comparison_detail_view
        )

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

        # Comparison tab
        comparison_tab = QWidget()
        comparison_tab_layout = QVBoxLayout(comparison_tab)

        self.comparison_figure = Figure(figsize=(10, 5))
        self.comparison_canvas = FigureCanvas(self.comparison_figure)
        comparison_tab_layout.addWidget(self.comparison_canvas)

        self.comparison_table = QTableWidget()
        self.comparison_table.setAlternatingRowColors(True)
        comparison_tab_layout.addWidget(self.comparison_table)

        self.comparison_tab_index = self.tabs.addTab(
            comparison_tab,
            "Comparison"
        )

        # Single-strategy mode starts with the Comparison tab unavailable.
        self.tabs.setTabEnabled(self.comparison_tab_index, False)

        # A disabled Qt tab normally ignores clicks entirely. This filter lets
        # us explain why Portfolio cannot be opened in comparison mode.
        self.disabled_tab_click_filter = DisabledTabClickFilter(self)
        self.tabs.tabBar().installEventFilter(
            self.disabled_tab_click_filter
        )

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
            commission = self.commission_input.value()
            slippage = self.slippage_input.value() / 100

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

            if self.mode_combo.currentText() == "Single Strategy":
                self._run_single_backtest(
                    market_df,
                    ticker,
                    start_date,
                    end_date,
                    initial_capital,
                    interval,
                    commission,
                    slippage,
                )
            else:
                self._run_comparison_backtest(
                    market_df,
                    ticker,
                    start_date,
                    end_date,
                    initial_capital,
                    interval,
                    commission,
                    slippage,
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

    def _run_single_backtest(
        self,
        market_df,
        ticker,
        start_date,
        end_date,
        initial_capital,
        interval,
        commission,
        slippage,
    ):
        strategy = self._create_selected_strategy()

        strategy_df = strategy.generateSignals(market_df)

        if strategy_df.empty:
            raise ValueError(
                "Not enough data for the selected strategy and timeframe."
            )

        backtester = Backtester(
            initial_capital,
            commission=commission,
            slippage=slippage,
        )
        portfolio_df = backtester.run(
            strategy_df,
            strategy.execution_delay,
        )

        calculator = MetricsCalculator()
        metrics_df = calculator.calculateMetrics(
            portfolio_df,
            interval,
        )

        self.portfolio_df = portfolio_df
        self.metrics_df = metrics_df
        self.portfolio_results = None
        self.comparison_df = None

        self.detail_strategy_widget.setVisible(False)

        # Single-strategy results:
        # Portfolio / Signals / Trades / Metrics are available.
        # Comparison is disabled.
        for tab_index in range(4):
            self.tabs.setTabEnabled(tab_index, True)

        self.tabs.setTabEnabled(self.comparison_tab_index, False)

        self._update_results(
            ticker=ticker,
            strategy_name=self.strategy_combo.currentText(),
            start_date=start_date,
            end_date=end_date,
            commission=commission,
            slippage=slippage,
        )

    def _run_comparison_backtest(
        self,
        market_df,
        ticker,
        start_date,
        end_date,
        initial_capital,
        interval,
        commission,
        slippage,
    ):
        strategies = self._create_comparison_strategies()

        if len(strategies) < 2:
            raise ValueError(
                "Select at least two strategies to compare."
            )

        comparison_engine = ComparisonEngine(
            market_df,
            initial_capital=initial_capital,
            commission=commission,
            slippage=slippage,
            interval=interval,
            **strategies,
        )

        portfolio_results, comparison_df = (
            comparison_engine.runStrategies()
        )

        self.portfolio_results = portfolio_results
        self.comparison_df = comparison_df
        self.portfolio_df = None
        self.metrics_df = None

        # In comparison mode, the individual Portfolio tab is redundant:
        # the Comparison tab already shows all portfolio curves together.
        self.tabs.setTabEnabled(0, False)
        self.tabs.setTabEnabled(1, True)   # Signals
        self.tabs.setTabEnabled(2, True)   # Trades
        self.tabs.setTabEnabled(3, True)   # Metrics
        self.tabs.setTabEnabled(self.comparison_tab_index, True)

        # Let the user inspect Signals / Trades / Metrics for any
        # strategy that participated in the comparison.
        self.detail_strategy_combo.blockSignals(True)
        self.detail_strategy_combo.clear()
        self.detail_strategy_combo.addItems(
            list(self.portfolio_results.keys())
        )
        self.detail_strategy_combo.blockSignals(False)
        self.detail_strategy_widget.setVisible(True)

        if self.detail_strategy_combo.count() > 0:
            self._update_comparison_detail_view(
                self.detail_strategy_combo.currentText()
            )

        self._update_comparison_results(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            commission=commission,
            slippage=slippage,
        )

    def _create_comparison_strategies(self):
        strategies = {}

        if self.compare_buy_hold.isChecked():
            strategies["Buy & Hold"] = BuyHold()

        if self.compare_ma.isChecked():
            short_window = self.ma_short_input.value()
            long_window = self.ma_long_input.value()

            if short_window >= long_window:
                raise ValueError(
                    "The short MA window must be smaller than "
                    "the long MA window."
                )

            strategies["MA Crossover"] = MaCrossover(
                short_window,
                long_window,
            )

        if self.compare_rsi.isChecked():
            lower = self.rsi_lower_input.value()
            upper = self.rsi_upper_input.value()

            if lower >= upper:
                raise ValueError(
                    "The RSI buy threshold must be below "
                    "the sell threshold."
                )

            strategies["RSI"] = Rsi(
                self.rsi_window_input.value(),
                lower,
                upper,
            )

        if self.compare_bollinger.isChecked():
            strategies["Bollinger Bands"] = BollingerBands(
                self.bb_window_input.value(),
                self.bb_deviation_input.value(),
            )

        if self.compare_breakout.isChecked():
            strategies["Breakout Momentum"] = BreakoutMomentum(
                self.breakout_high_input.value(),
                self.breakout_low_input.value(),
            )

        return strategies

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
        commission,
        slippage,
    ):
        metrics = self.metrics_df.iloc[0]

        self.summary_label.setText(
            f"{ticker} | {strategy_name} | {start_date} to {end_date} | "
            f"Commission ${commission:,.2f} | Slippage {slippage * 100:.3f}%"
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

        buys = self.portfolio_df[self.portfolio_df["Trade_execution"] == 1]
        sells = self.portfolio_df[self.portfolio_df["Trade_execution"] == -1]

        ax.scatter(
            buys.index,
            buys["Close"],
            marker="^",
            label="Buy",
            zorder=3,
            c='green'
        )

        ax.scatter(
            sells.index,
            sells["Close"],
            marker="v",
            label="Sell",
            zorder=3,
            c='red'
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
            self.portfolio_df["Trade_execution"] != 0
        ].copy()

        wanted_columns = [
            "Close",
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

        self.trades_table.setColumnCount(len(columns) + 2)
        display_headers = {
            "Close": "Market Price",
            "Shares": "Shares",
            "Cash": "Cash",
            "Total_value": "Total Value",
        }

        self.trades_table.setHorizontalHeaderLabels(
            ["Date", "Action"]
            + [display_headers.get(column, column) for column in columns]
        )
        self.trades_table.setRowCount(len(trades_df))

        for row_number, (index, row) in enumerate(trades_df.iterrows()):
            self.trades_table.setItem(
                row_number,
                0,
                QTableWidgetItem(str(index)),
            )

            action = (
                "BUY"
                if row["Trade_execution"] == 1
                else "SELL"
            )

            self.trades_table.setItem(
                row_number,
                1,
                QTableWidgetItem(action),
            )

            for column_number, column in enumerate(columns, start=2):
                value = row[column]

                if isinstance(value, float):
                    value_text = f"{value:,.4f}"
                else:
                    value_text = str(value)

                self.trades_table.setItem(
                    row_number,
                    column_number,
                    QTableWidgetItem(value_text),
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

    def _update_comparison_detail_view(self, strategy_name):
        if (
            not strategy_name
            or self.portfolio_results is None
            or strategy_name not in self.portfolio_results
        ):
            return

        # Reuse the same individual-result widgets as single mode.
        self.portfolio_df = self.portfolio_results[strategy_name]

        if (
            self.comparison_df is not None
            and "Strategy" in self.comparison_df.columns
        ):
            strategy_metrics = self.comparison_df[
                self.comparison_df["Strategy"] == strategy_name
            ].copy()

            if not strategy_metrics.empty:
                self.metrics_df = (
                    strategy_metrics
                    .drop(columns=["Strategy"])
                    .reset_index(drop=True)
                )

        ticker = self.ticker_input.text().strip().upper()

        self._plot_signals(ticker, strategy_name)
        self._populate_trades_table()
        self._populate_metrics_table()

    def _update_comparison_results(
        self,
        ticker,
        start_date,
        end_date,
        commission,
        slippage,
    ):
        self.summary_label.setText(
            f"{ticker} | Strategy Comparison | {start_date} to {end_date} | "
            f"Commission ${commission:,.2f} | Slippage {slippage * 100:.3f}%"
        )

        if self.comparison_df is not None and not self.comparison_df.empty:
            if "Ending_value" in self.comparison_df.columns:
                best_row = self.comparison_df.loc[
                    self.comparison_df["Ending_value"].idxmax()
                ]
                self._set_metric(
                    self.ending_value_label,
                    "Best Ending Value",
                    f"{best_row['Strategy']}: "
                    f"${best_row['Ending_value']:,.2f}",
                )

            if "Cumulative_return%" in self.comparison_df.columns:
                best_row = self.comparison_df.loc[
                    self.comparison_df["Cumulative_return%"].idxmax()
                ]
                self._set_metric(
                    self.return_label,
                    "Best Return",
                    f"{best_row['Strategy']}: "
                    f"{best_row['Cumulative_return%']:.2f}%",
                )

            if "Sharpe_ratio" in self.comparison_df.columns:
                best_row = self.comparison_df.loc[
                    self.comparison_df["Sharpe_ratio"].idxmax()
                ]
                self._set_metric(
                    self.sharpe_label,
                    "Best Sharpe",
                    f"{best_row['Strategy']}: "
                    f"{best_row['Sharpe_ratio']:.3f}",
                )

            if "Max_drawdown%" in self.comparison_df.columns:
                best_row = self.comparison_df.loc[
                    self.comparison_df["Max_drawdown%"].idxmax()
                ]
                self._set_metric(
                    self.drawdown_label,
                    "Smallest Drawdown",
                    f"{best_row['Strategy']}: "
                    f"{best_row['Max_drawdown%']:.2f}%",
                )

        self._plot_comparison()
        self._populate_comparison_table()
        self.tabs.setCurrentIndex(self.comparison_tab_index)

    def _plot_comparison(self):
        self.comparison_figure.clear()
        ax = self.comparison_figure.add_subplot(111)

        for name, portfolio_df in self.portfolio_results.items():
            ax.plot(
                portfolio_df.index,
                portfolio_df["Total_value"],
                label=name,
            )

        ax.set_title("Strategy Portfolio Comparison")
        ax.set_xlabel("Date")
        ax.set_ylabel("Portfolio Value ($)")
        ax.grid(True)
        ax.legend()

        self.comparison_figure.tight_layout()
        self.comparison_canvas.draw()

    def _populate_comparison_table(self):
        df = self.comparison_df

        self.comparison_table.setSortingEnabled(False)
        self.comparison_table.clear()
        self.comparison_table.setColumnCount(len(df.columns))
        self.comparison_table.setHorizontalHeaderLabels(
            [str(column) for column in df.columns]
        )
        self.comparison_table.setRowCount(len(df))

        for row_number, (_, row) in enumerate(df.iterrows()):
            for column_number, column in enumerate(df.columns):
                value = row[column]

                if isinstance(value, float):
                    text = f"{value:,.4f}"
                else:
                    text = str(value)

                self.comparison_table.setItem(
                    row_number,
                    column_number,
                    QTableWidgetItem(text),
                )

        self.comparison_table.resizeColumnsToContents()
        self.comparison_table.setSortingEnabled(True)

    # =====================================================
    # Export
    # =====================================================

    def export_results(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Choose Export Folder",
        )

        if not directory:
            return

        ticker = self.ticker_input.text().strip().upper()
        output_directory = Path(directory)

        if self.mode_combo.currentText() == "Single Strategy":
            if self.portfolio_df is None or self.metrics_df is None:
                return

            strategy_name = (
                self.strategy_combo.currentText()
                .lower()
                .replace(" ", "_")
                .replace("&", "and")
            )

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

        else:
            if (
                self.portfolio_results is None
                or self.comparison_df is None
            ):
                return

            comparison_file = (
                output_directory
                / f"{ticker}_strategy_comparison.csv"
            )
            self.comparison_df.to_csv(
                comparison_file,
                index=False,
            )

            for name, portfolio_df in self.portfolio_results.items():
                safe_name = (
                    name.lower()
                    .replace(" ", "_")
                    .replace("&", "and")
                )

                portfolio_file = (
                    output_directory
                    / f"{ticker}_{safe_name}_portfolio.csv"
                )

                portfolio_df.to_csv(portfolio_file)

        QMessageBox.information(
            self,
            "Export Complete",
            f"Results saved to:\n{output_directory}",
        )

    # =====================================================
    # UI helpers
    # =====================================================

    def _update_mode_ui(self, mode):
        comparison_mode = mode == "Compare Strategies"

        # Keep the strategy selector/parameter editor visible in both modes.
        # In comparison mode, it chooses which strategy's parameters
        # are currently being edited.
        self.strategy_box.setVisible(True)
        self.comparison_box.setVisible(comparison_mode)

        if comparison_mode:
            self.strategy_box.setTitle("Strategy Parameters")

            # Portfolio is an individual-strategy view, so it is not used
            # in comparison mode. Make that visually explicit as well as
            # disabling the tab.
            self.tabs.setTabEnabled(0, False)
            self.tabs.setTabText(
                0,
                "✕ Portfolio — Single Strategy Only"
            )
            self.tabs.setTabToolTip(
                0,
                "Disabled in Compare Strategies mode. "
                "Click the tab for more information."
            )

            self.tabs.setTabEnabled(self.comparison_tab_index, True)

            # Detail tabs become useful once comparison results exist.
            has_comparison_results = self.portfolio_results is not None
            self.tabs.setTabEnabled(1, has_comparison_results)
            self.tabs.setTabEnabled(2, has_comparison_results)
            self.tabs.setTabEnabled(3, has_comparison_results)

            self.detail_strategy_widget.setVisible(
                has_comparison_results
            )

            if self.tabs.currentIndex() == 0:
                self.tabs.setCurrentIndex(self.comparison_tab_index)

            self.summary_label.setText(
                "Select the strategies to compare. Use Strategy Parameters "
                "to configure them, then run the backtest. Afterward, use "
                "'View strategy details' to inspect each strategy's signals, "
                "trades and metrics."
            )

        else:
            self.strategy_box.setTitle("Strategy")

            # Restore the normal Portfolio tab label in single mode.
            self.tabs.setTabText(0, "Portfolio")
            self.tabs.setTabToolTip(0, "")

            # Individual-result tabs are valid in single mode.
            for tab_index in range(4):
                self.tabs.setTabEnabled(tab_index, True)

            self.tabs.setTabEnabled(self.comparison_tab_index, False)
            self.detail_strategy_widget.setVisible(False)

            if self.tabs.currentIndex() == self.comparison_tab_index:
                self.tabs.setCurrentIndex(0)

            self.summary_label.setText(
                "Choose a ticker, date range and strategy, "
                "then run a backtest."
            )

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