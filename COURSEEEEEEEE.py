import yfinance as yf
import csv
import os
from abc import ABC, abstractmethod

# 1. ABSTRACTION - Base class for all instruments
class FinancialInstrument(ABC):
    def __init__(self, ticker, label, quantity=0, buy_price=0):
        self.ticker = ticker.upper()
        self.label = label
        self.name = "Fetching..." # Placeholder for the real name
        self.quantity = float(quantity)
        self.buy_price = float(buy_price)
        # 2. ENCAPSULATION - Private price attribute
        self.__current_price = 0.0 

    @abstractmethod
    def fetch_data(self):
        """Fetches live price and full name from API"""
        pass

    def set_price(self, price):
        if price is not None and price >= 0:
            self.__current_price = float(price)
        else:
            self.__current_price = 0.0

    def get_price(self):
        return self.__current_price

    def get_total_cost(self):
        return self.quantity * self.buy_price

    def get_market_value(self):
        return self.quantity * self.__current_price

    def get_profit_loss(self):
        return self.get_market_value() - self.get_total_cost()

# 3. INHERITANCE - Specialized asset classes
class Stock(FinancialInstrument):
    def __init__(self, ticker, qty=0, buy=0):
        super().__init__(ticker, "STOCK", qty, buy)
    def fetch_data(self):
        try:
            t = yf.Ticker(self.ticker)
            self.set_price(t.fast_info.last_price)
            self.name = t.info.get('longName', self.ticker)
        except: self.set_price(0.0)

class Crypto(FinancialInstrument):
    def __init__(self, ticker, qty=0, buy=0):
        symbol = f"{ticker.upper()}-USD" if "-USD" not in ticker.upper() else ticker
        super().__init__(symbol, "CRYPTO", qty, buy)
    def fetch_data(self):
        try:
            t = yf.Ticker(self.ticker)
            self.set_price(t.fast_info.last_price)
            self.name = t.info.get('shortName', self.ticker)
        except: self.set_price(0.0)

class Bond(FinancialInstrument):
    def __init__(self, ticker, qty=0, buy=0):
        super().__init__(ticker, "BOND", qty, buy)
    def fetch_data(self):
        try:
            t = yf.Ticker(self.ticker)
            self.set_price(t.fast_info.last_price)
            self.name = t.info.get('shortName', "Treasury Bond")
        except: self.set_price(0.0)

class Commodity(FinancialInstrument):
    def __init__(self, ticker, qty=0, buy=0):
        symbol = ticker if "=F" in ticker.upper() else f"{ticker.upper()}=F"
        super().__init__(symbol, "COMMODITY", qty, buy)
    def fetch_data(self):
        try:
            t = yf.Ticker(self.ticker)
            self.set_price(t.fast_info.last_price)
            self.name = t.info.get('shortName', "Commodity Future")
        except: self.set_price(0.0)

class Forex(FinancialInstrument):
    def __init__(self, ticker, qty=0, buy=0):
        symbol = ticker if "=X" in ticker.upper() else f"{ticker.upper()}=X"
        super().__init__(symbol, "FOREX", qty, buy)
    def fetch_data(self):
        try:
            t = yf.Ticker(self.ticker)
            self.set_price(t.fast_info.last_price)
            self.name = t.info.get('shortName', self.ticker)
        except: self.set_price(0.0)

class ETF(FinancialInstrument):
    def __init__(self, ticker, qty=0, buy=0):
        super().__init__(ticker, "ETF", qty, buy)
    def fetch_data(self):
        try:
            t = yf.Ticker(self.ticker)
            self.set_price(t.fast_info.last_price)
            self.name = t.info.get('longName', self.ticker)
        except: self.set_price(0.0)

# 4. SINGLETON DESIGN PATTERN
class PortfolioManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortfolioManager, cls).__new__(cls)
            cls._instance.portfolio = []
        return cls._instance

    def add_item(self, instrument):
        for existing in self.portfolio:
            if existing.ticker == instrument.ticker:
                existing.fetch_data()
                return False
        instrument.fetch_data()
        self.portfolio.append(instrument)
        return True

    # 6. FILE MANAGEMENT
    def save_to_csv(self, filename="portfolio.csv"):
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Ticker", "Qty", "BuyPrice"])
                for item in self.portfolio:
                    writer.writerow([item.label, item.ticker, item.quantity, item.buy_price])
            print(f"\n[SUCCESS] Portfolio saved to {filename}")
        except Exception as e: print(f"[ERROR] Save failed: {e}")

    def load_from_csv(self, filename="portfolio.csv"):
        if not os.path.exists(filename): return
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    t, tick = row["Type"], row["Ticker"]
                    q, b = float(row["Qty"]), float(row["BuyPrice"])
                    if t == "STOCK": self.add_item(Stock(tick, q, b))
                    elif t == "CRYPTO": self.add_item(Crypto(tick, q, b))
                    elif t == "BOND": self.add_item(Bond(tick, q, b))
                    elif t == "COMMODITY": self.add_item(Commodity(tick, q, b))
                    elif t == "FOREX": self.add_item(Forex(tick, q, b))
                    elif t == "ETF": self.add_item(ETF(tick, q, b))
        except Exception as e: print(f"[ERROR] Loading failed: {e}")

# 7. POLYMORPHISM - Table Dashboard
def display_dashboard(manager):
    print("\n" + "="*120)
    print(f"{'TYPE':<10} | {'TICKER':<10} | {'NAME':<30} | {'QTY':<8} | {'MARKET':<10} | {'P/L ($)':<10}")
    print("-" * 120)
    total_val, total_pl = 0, 0
    for item in manager.portfolio:
        pl = item.get_profit_loss()
        total_pl += pl
        total_val += item.get_market_value()
        # Display the name (truncated if too long for the table)
        print(f"{item.label:<10} | {item.ticker:<10} | {item.name[:28]:<30} | {item.quantity:<8.2f} | {item.get_price():<10.2f} | {pl:>10.2f}")
    print("-" * 120)
    print(f"TOTAL VALUE: {total_val:>10.2f} USD | TOTAL PROFIT/LOSS: {total_pl:>10.2f} USD")
    print("="*120)

if __name__ == "__main__":
    manager = PortfolioManager()
    
    # Load data from file first
    manager.load_from_csv()
    
    # Add items (if they already exist in CSV, they will just be updated)
    manager.add_item(Stock("AAPL", qty=10, buy=170))
    manager.add_item(Crypto("BTC", qty=0.1, buy=40000))
    manager.add_item(Commodity("GC", qty=2, buy=2000))
    manager.add_item(Bond("ZT=F", qty=5, buy=100))
    manager.add_item(Forex("EURUSD", qty=1000, buy=1.08))
    manager.add_item(ETF("SPY", qty=10, buy=450))
    
    # Final output
    display_dashboard(manager)
    manager.save_to_csv()
