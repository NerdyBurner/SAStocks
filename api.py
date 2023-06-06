#Build as of 6.5.23
import requests
import logging
from config import Config
from typing import Union

class Api:
    def __init__(self):
        self.polygon_api_key = Config.POLYGON_API_KEY
        self.openai_api_key = Config.OPENAI_API_KEY

    def fetch_tickers(self):
        try:
            response = requests.get(f'https://api.polygon.io/v3/reference/tickers?apiKey={self.polygon_api_key}')
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Polygon API response: {data}")
            return [item['ticker'] for item in data['results']]
        except Exception as e:
            logging.error(f"Error fetching tickers: {str(e)}")
            return []

    def fetch_news(self, ticker):
        try:
            response = requests.get(f'https://api.polygon.io/v1/meta/symbols/{ticker}/news?apiKey={self.polygon_api_key}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching news for ticker {ticker}: {str(e)}")
            return []

    def fetch_financials(self, ticker):
        try:
            response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/2023-01-01/2023-06-01?apiKey={self.polygon_api_key}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching financials for ticker {ticker}: {str(e)}")
            return []


    def fetch_rsi(self, ticker):
        try:
            response = requests.get(f'https://api.polygon.io/v1/indicators/rsi/{ticker}?timespan=day&adjusted=true&window=14&series_type=close&order=desc&apiKey={self.polygon_api_key}')
            response.raise_for_status()
            data = response.json()
            # Get the list of RSI values
            rsi_values = [item['value'] for item in data['results']['values']]
            # Calculate and return the average RSI value
            average_rsi = sum(rsi_values) / len(rsi_values)
            return average_rsi
        except Exception as e:
            logging.error(f"Error fetching RSI for {ticker}: {str(e)}")
            return 0


    def fetch_macd(self, ticker: str) -> Union[float, int]:
        try:
            response = requests.get(f'https://api.polygon.io/v1/indicators/macd/{ticker}?timespan=day&adjusted=true&fast=12&slow=26&signal=9&series_type=close&order=desc&apiKey={self.polygon_api_key}')
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching MACD for {ticker}: {str(e)}")
            return 0
        json_response = response.json()
        print(json_response)
        return json_response.get('results', [{}])[0].get('histogram', 0)


    def fetch_prices(self, ticker: str, start_date: str, end_date: str) -> dict:
        try:
            response = requests.get(f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?apiKey={self.polygon_api_key}')
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching prices for {ticker}: {str(e)}")
            if response:
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.content}")
            return {}
        return response.json()

