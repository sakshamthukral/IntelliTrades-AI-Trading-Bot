from lumibot.brokers import Alpaca #  Alpaca is gonna be our broker
from lumibot.backtesting import YahooDataBacktesting # We are going to use Yahoo Finance data for backtesting
from lumibot.strategies.strategy import Strategy # Strategy will be out actual trading bot
from lumibot.traders import Trader # Trader will be our trading bot and give us the deployment capability if we want to run it live
from datetime import datetime

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

class MLTrader(Strategy):
    def initialize(self, symbol:str="SPY"): # Setup: This method will run once at the beginning of the backtesting/trading
        self.symbol = symbol
        self.sleeptime = "24H" # basically dictates how often we want to run our trading logic
        self.last_trade = None # if we want to undo some of our trades or buys, we can keep track of our last trade
    
    def poition_sizing(self): # Position Sizing: How much we want to buy or sell. Position management and cash management are absolutely critical steps
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        

    
    def on_trading_iteration(self): # Trading Logic: Will run everytime we get a tick. Everytime we get a new data from our data source, we are gonna be able to execute a trade or do something with it.
        if self.last_trade == None:
            order = self.create_order(
                self.symbol,
                10, # how many of symbols we want to buy
                "buy", # buy or sell
                type="market" # market or limit
            )
            self.submit_order(order)
            self.last_trade = "buy"

start_date = datetime(2023, 12, 15)
end_date = datetime(2023, 12, 31)

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name="mlstrat", broker=broker, parameters={"symbol": "SPY"})

strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol": "SPY"}
)