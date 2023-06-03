#Build as of 6.3.23
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
            response = requests.get(f'https://api.polygon.io/v1/meta/symbols/{ticker}/news?published_utc=5/26/23&apiKey={self.polygon_api_key}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching news for {ticker}: {str(e)}")
            return {}

    def fetch_rsi(self, ticker: str) -> dict:
        url = f"https://api.polygon.io/v1/indicators/rsi/{ticker}?timespan=day&adjusted=true&window=14&series_type=close&order=desc&apiKey={self.polygon_api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def fetch_macd(self, ticker: str) -> dict:
        url = f"https://api.polygon.io/v1/indicators/macd/{ticker}?timespan=day&adjusted=true&short_window=12&long_window=26&signal_window=9&series_type=close&order=desc&apiKey={self.polygon_api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def fetch_prices(self, ticker: str, start_date: str, end_date: str) -> dict:
        try:
            response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?apiKey={self.polygon_api_key}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching prices for {ticker}: {str(e)}")
            return {}
