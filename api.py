import requests
from config import Config

class Api:
    def fetch_tickers(self):
        with open(Config.TICKERS_FILE, 'r') as file:
            tickers = file.read().splitlines()
        return tickers

    def fetch_news(self, ticker):
        response = requests.get(f'https://api.polygon.io/v1/meta/symbols/{ticker}/news?apiKey={Config.POLYGON_API_KEY}')
        response.raise_for_status()
        return response.json()

