from lumibot.brokers import Alpaca #  Alpaca is gonna be our broker
from lumibot.backtesting import YahooDataBacktesting # We are going to use Yahoo Finance data for backtesting
from lumibot.strategies.strategy import Strategy # Strategy will be our actual trading bot
from lumibot.traders import Trader # Trader will give us the deployment capability if we want to run it live
from datetime import datetime
from alpaca_trade_api import REST # REST is the API that we are going to use to interact with Alpaca

from datetime import timedelta
from finbert_utils import estimate_sentiment

# APCA-API-KEY-ID = "AKIG4DG8T44T4D3T52SN"
# APCA-API-SECRET-KEY = "2yDuMld8XY6D2PUgtr9jBiReMSt6cYThaWqYt0eO"
# BASE_URL = "https://paper-api.alpaca.markets"


APCA_API_KEY_ID = "PKIYSY34H4BF1QA7REW5"
APCA_API_SECRET_KEY = "DRhMsZ9MoeFsCdVCQfOl1MpDQKrJAzlEdyFq0q4M"
BASE_URL = "https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY": APCA_API_KEY_ID,
    "API_SECRET": APCA_API_SECRET_KEY,
    "PAPER": True,
}

class MLTrader(Strategy): # Backbone of our trading bot
    # Lifecycle methods:- initialize, position_sizing, on_trading_iteration

    def initialize(self, symbol:str="SPY", cash_at_risk:float=.5): # Setup: This method will run once at the beginning of the backtesting/trading
        self.symbol = symbol
        self.sleeptime = "24H" # basically dictates how often we want to run our trading logic
        self.last_trade = None # if we want to undo some of our trades or buys, we can keep track of our last trade
        self.cash_at_risk = cash_at_risk # how much of our cash we want to risk on each trade
        self.api = REST(base_url=BASE_URL, key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY)
    
    def position_sizing(self): # Position Sizing: How much we want to buy or sell. Position management and cash management are absolutely critical steps
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round((cash * self.cash_at_risk) / last_price, 0) # how many of the symbols we want to buy based on the cash we have and the price of the symbol
        return cash, last_price, quantity


    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - timedelta(days=3)
        return today.strftime("%Y-%m-%d"), three_days_prior.strftime("%Y-%m-%d")
    
    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment
    
    def on_trading_iteration(self): # Trading Logic: Will run everytime we get a tick. Everytime we get a new data from our data source, we are gonna be able to execute a trade or do something with it.
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()
        if cash > last_price: # if we have enough cash to buy
            if sentiment == "positive" and probability > .999:    
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity, # how many of symbols we want to buy
                    "buy", # buy or sell
                    # type="market" # market or limit
                    type="bracket",
                    take_profit_price=last_price * 1.20, # 20% profit
                    stop_loss_price=last_price * .95 # 5% loss
                )
                self.submit_order(order)
                self.last_trade = "buy"

            elif sentiment == "negative" and probability > .999:    
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity, # how many of symbols we want to buy
                    "buy", # buy or sell
                    # type="market" # market or limit
                    type="bracket",
                    take_profit_price=last_price * 0.8, # 1-0.2 i.e (100%-20%) = 80%(0.8) profit
                    stop_loss_price=last_price * 1.05 # 1+0.05 i.e (100%+5%) = 105%(1.05) loss
                )
                self.submit_order(order)
                self.last_trade = "sell"

start_date = datetime(2020, 1, 1)
end_date = datetime(2023, 12, 31)

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name="mlstrat", broker=broker, parameters={"symbol": "SPY", "cash_at_risk": .5})

strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol": "SPY", "cash_at_risk": .5}
)

# To deploy the strategy live
# trader = Trader()
# trader.add_strategy(strategy)
# trader.run_all()