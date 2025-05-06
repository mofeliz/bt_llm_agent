import os
from datetime import datetime, timedelta, UTC

from dotenv import load_dotenv, dotenv_values
import backtrader as bt
from tl_bt_adapter import (
    TLBackBroker,
    TLLiveBroker,
    TLData,
)

from bt_llm_advisory import BacktraderLLMAdvisory
from bt_llm_advisory.advisors import (
    BacktraderStrategyAdvisor,
    BacktraderPersonaAdvisor,
    BacktraderFeedbackAdvisor,
    BacktraderCandlePatternAdvisor,
    BacktraderTechnicalAnalysisAdvisor,
    BacktraderTrendAdvisor,
)

load_dotenv()

bot_advisory = BacktraderLLMAdvisory(
    model_provider_name=os.getenv("LLM_MODEL_PROVIDER"),
    model_name=os.getenv("LLM_MODEL"),
    model_config={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")},
    advisors=[
        BacktraderTrendAdvisor(
            long_ma_period=25,
            short_ma_period=10,
            lookback_period=10,
            add_all_data_feeds=True,
        ),
        BacktraderCandlePatternAdvisor(lookback_period=10, add_all_data_feeds=True),
        BacktraderStrategyAdvisor(),
        BacktraderTechnicalAnalysisAdvisor(),
        BacktraderFeedbackAdvisor(),
        # BacktraderPersonaAdvisor("Technical advisor", "intraday trader"),
        # BacktraderPersonaAdvisor(
        #     "Warren Buffett",
        #     (
        #         "A long-term fundamental investor who avoids market noise and focuses on intrinsic value.\n"
        #         "Preferred Investment Types: stocks, private equity\n"
        #         "Preferred Timeframes: monthly to yearly\n"
        #         "Special Knowledge: business valuation, economic moats, compound interest\n"
        #     ),
        # ),
        # BacktraderPersonaAdvisor(
        #     "Paul Tudor Jones",
        #     (
        #         "A tactical trader with an edge in reading market psychology and momentum.\n"
        #         "Preferred Investment Types: forex, commodities, equities\n"
        #         "Preferred Timeframes: 4H to daily\n"
        #         "Special Knowledge: macro fundamentals, technical divergence, volatility spikes\n"
        #     ),
        # ),
        # BacktraderPersonaAdvisor(
        #     "Stanley Druckenmiller",
        #     (
        #         "An adaptive macro investor with a strong sense for capital flow shifts.\n"
        #         "Preferred Investment Types: forex, equities, crypto\n"
        #         "Preferred Timeframes: swing (daily-weekly)\n"
        #         "Special Knowledge: macro narrative interpretation, position sizing, liquidity cycles\n"
        #     ),
        # ),
        # BacktraderPersonaAdvisor(
        #     "Jesse Livermore",
        #     (
        #         "A classic trend follower and breakout trader.\n"
        #         "Preferred Investment Types: stocks, commodities\n"
        #         "Preferred Timeframes: daily to weekly\n"
        #         "Special Knowledge: price action, market timing, pyramiding\n"
        #     ),
        # ),
        # BacktraderPersonaAdvisor(
        #     "Linda Raschke",
        #     (
        #         "A short-term technical trader who thrives in fast-moving markets.\n"
        #         "Preferred Investment Types: futures, forex\n"
        #         "Preferred Timeframes: 15-min to 4H\n"
        #         "Special Knowledge: market structure, oscillator timing, mean-reversion setups\n"
        #     ),
        # ),
        # BacktraderPersonaAdvisor(
        #     "Peter Brandt",
        #     (
        #         "A disciplined classical chartist focusing on well-defined pattern setups.\n"
        #         "Preferred Investment Types: commodities, crypto, forex\n"
        #         "Preferred Timeframes: daily to weekly\n"
        #         "Special Knowledge: chart patterns, breakout confirmation, risk management\n"
        #     ),
        # ),
        # BacktraderPersonaAdvisor(
        #     "Michael Burry",
        #     (
        #         "A contrarian value investor with a specialty in crisis detection.\n"
        #         "Preferred Investment Types: equities, CDS, macro derivatives\n"
        #         "Preferred Timeframes: multi-week to multi-year\n"
        #         "Special Knowledge: forensic analysis, systemic risk detection\n"
        #     ),
        # ),
        # BacktraderPersonaAdvisor(
        #     "Richard Dennis",
        #     (
        #         "A trend-following system trader using strict entry/exit rules.\n"
        #         "Preferred Investment Types: futures, commodities, forex\n"
        #         "Preferred Timeframes: daily\n"
        #         "Special Knowledge: Turtle Trading rules, volatility-based risk control, position scaling\n"
        #     ),
        # ),
    ],
    max_concurrency=2,
)


class TestStrategy(bt.Strategy):

    def __init__(self):
        bot_advisory.init_strategy(self)
        self.ma = bt.indicators.SMA(period=10)
        self.ma2 = bt.indicators.SMA(period=40)

    def stop(self):
        print("STOP")

    def prenext(self):
        print("PRENEXT", self.data0.datetime.datetime(0), len(self.data0))

    def next(self):
        if self.data0.isdelayed():
            print("DELAYED DATA", len(self.data0))
            return
        print("NEXT", self.data0.datetime.datetime(0), len(self.data0))

        advisory_response = bot_advisory.get_advisory()

        print("\n", "ADDITIONAL DATA", "-" * 80, "\n")
        print(advisory_response.state.data)

        print("\n", "MESSAGES", "-" * 80, "\n")
        for message in advisory_response.state.messages:
            print(f"{message.__class__.__name__} {message.name}: {message.content}")

        print("\n", "CONVERSATIONS", "-" * 80, "\n")
        for advisor_name, conversion in advisory_response.state.conversations.items():
            for message in conversion:
                print("\n", advisor_name, "-" * 40)
                print(f"{message.__class__.__name__} {message.name}: {message.content}")

        print("\n", "SIGNALS", "-" * 80, "\n")
        for advisor_name, signal in advisory_response.state.signals.items():
            print(
                "\n"
                f"Advisor: '{advisor_name}'"
                f" Signal: '{signal.signal}'"
                f" Confidence: '{signal.confidence}'"
                f" Reasoning: '{signal.reasoning}'"
                "\n"
            )

        print(
            "-" * 80,
            "\n",
            advisory_response.state.messages[0].content,
            "\n",
            "\n",
            advisory_response.advise,
            "\n",
            "-" * 80,
            "\n\n",
        )

    def notify_trade(self, trade):
        print(trade)


def create_cerebro():

    config = dotenv_values()

    cerebro = bt.Cerebro(quicknotify=True, stdstats=False)
    broker = TLLiveBroker(
        environment=config.get("tl_environment", "demo"),
        username=config.get("tl_email", ""),
        password=config.get("tl_password", ""),
        server=config.get("tl_server", ""),
        acc_num=int(config.get("tl_acc_num", 0)),
        log_level="info",
        disk_cache_location="./dc",
        # convert_currencies=True,
        # convert_currencies_cache_resolution=60,
        # quicknotify=True,
    )
    cerebro.setbroker(broker)

    # create data
    # from and to date to fetch historical data only
    # from_date = datetime.now(UTC) - timedelta(days=14)
    # to_date = datetime.now(UTC)

    timeframe = bt.TimeFrame.Minutes
    compression = 1
    compression_1 = 5
    data = TLData(
        dataname="BTCUSD",
        timeframe=timeframe,
        compression=compression,
        # fromdate=from_date.replace(tzinfo=None),
        # todate=to_date.replace(tzinfo=None),
        num_prefill_candles=400,
        start_live_data=True,
    )
    # when data switches to live, ticks will be used, either resampledata or replaydata
    cerebro.resampledata(data, timeframe=timeframe, compression=compression)
    cerebro.resampledata(data, timeframe=timeframe, compression=compression_1)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addstrategy(TestStrategy)
    return cerebro


try:
    cerebro = create_cerebro()
    cerebro.run()
except KeyboardInterrupt as e:
    print(e)
finally:
    cerebro.runstop()
    print("Cerebro stopped.")
