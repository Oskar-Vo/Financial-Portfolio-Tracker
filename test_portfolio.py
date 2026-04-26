import unittest
# Pakeitėme importą, kad jis atitiktų tavo failo pavadinimą
from OOPCoursework import PortfolioManager, Stock, Crypto

class TestFinancialPortfolio(unittest.TestCase):
    def setUp(self):
        """Runs before each test - starts with a clean portfolio"""
        self.manager = PortfolioManager()
        self.manager.portfolio = [] 

    def test_singleton(self):
        """Check: Is PortfolioManager a true Singleton?"""
        another_manager = PortfolioManager()
        self.assertIs(self.manager, another_manager, "Singleton failed!")

    def test_encapsulation(self):
        """Check: Does price protection work?"""
        s = Stock("AAPL")
        s.set_price(-500) # Bandome įvesti nesąmoningą kainą
        self.assertEqual(s.get_price(), 0.0, "Encapsulation failed: negative price allowed!")

    def test_profit_calculation(self):
        """Check: Is the math for Profit/Loss correct?"""
        # Perkam 2 vienetus po 1000$ (viso 2000$)
        # Dabartinė kaina 1500$ (viso 3000$)
        # Pelnas turi būti 1000$
        s = Stock("TEST", qty=2, buy=1000)
        s.set_price(1500)
        self.assertEqual(s.get_profit_loss(), 1000.0, "Math failed!")

    def test_crypto_ticker_format(self):
        """Check: Does crypto auto-format ticker?"""
        c = Crypto("BTC")
        self.assertIn("BTC-USD", c.ticker)

if __name__ == '__main__':
    unittest.main()
