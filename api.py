
import requests
from config import Config
from polygon import RESTClient

class Api:
    def __init__(self, polygon_api_key: str, tickers_file: str):
        self.polygon_api_key = polygon_api_key
        self.tickers_file = tickers_file

    def fetch_tickers(self) -> list:
        try:
            with open(self.tickers_file, 'r') as file:
                tickers = file.read().splitlines()
        except Exception as e:
            print(f"Error reading tickers file: {str(e)}")
            tickers = []
        return tickers

    def fetch_news(self, ticker: str) -> dict:
        try:
            response = requests.get(f'https://api.polygon.io/v1/meta/symbols/{ticker}/news?apiKey={self.polygon_api_key}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching news for {ticker}: {str(e)}")
            return {}

    def fetch_rsi(self, ticker: str) -> dict:
        try:
            client = RESTClient(self.polygon_api_key)
            rsi = client.get_rsi(ticker)
            return rsi
        except Exception as e:
            print(f"Error fetching RSI for {ticker}: {str(e)}")
            return {}

    def fetch_macd(self, ticker: str) -> dict:
        try:
            client = RESTClient(self.polygon_api_key)
            macd = client.get_macd(ticker)
            return macd
        except Exception as e:
            print(f"Error fetching MACD for {ticker}: {str(e)}")
            return {}

    def fetch_prices(self, ticker: str, start_date: str, end_date: str) -> dict:
        try:
            response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?apiKey={self.polygon_api_key}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching prices for {ticker}: {str(e)}")
            return {}
