import pandas as pd
from datetime import datetime, timedelta
from sqlite3 import dbapi2 as sqlite
from retrying import retry
import requests
from pandas.tseries.offsets import BDay

# Load API keys from CSV
keys_df = pd.read_csv('api_keys.csv')
polygon_key = keys_df['polygon_key'].values[0]

# Database connection for sentiment scores
database_filename = 'sentiment_scores.db'
connection = sqlite.connect(database_filename)

connection.cursor().execute('''
    CREATE TABLE IF NOT EXISTS sentiment_scores
    (date text, ticker text, vader_sentiment text, gpt_sentiment text, gpt_response text,
        historical_price_high real, historical_price_low real, historical_price_avg real, aggregated_score real,
        recent_price real, rsi real, macd real)
''')

@retry(stop_max_attempt_number=7, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def requests_get_with_retry(url):
    response = requests.get(url)
    response.raise_for_status()  # Raises stored HTTPError, if one occurred
    return response

def get_rsi(ticker):
    rsi_url = f"https://api.polygon.io/v1/indicators/rsi/{ticker}?apiKey={polygon_key}"
    rsi_response = requests_get_with_retry(rsi_url)
    if rsi_response.status_code == 200:
        rsi_data = rsi_response.json()['results']['values']
        return rsi_data[0]['value'] if rsi_data else None  # Return the most recent value
    else:
        print(f"Error in get_rsi() for ticker {ticker}: {rsi_response.status_code}")
        return None

def get_macd(ticker):
    macd_url = f"https://api.polygon.io/v1/indicators/macd/{ticker}?apiKey={polygon_key}"
    macd_response = requests_get_with_retry(macd_url)
    if macd_response.status_code == 200:
        macd_data = macd_response.json()['results']['values']
        return macd_data[0]['value'] if macd_data else None  # Return the most recent value
    else:
        print(f"Error in get_macd() for ticker {ticker}: {macd_response.status_code}")
        return None

def get_historical_price(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    response = requests_get_with_retry(
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?apiKey={polygon_key}"
    )
    data = response.json()["results"]
    prices = [item["c"] for item in data]  # closing prices
    if prices:
        return max(prices), min(prices), sum(prices) / len(prices)
    else:
        return None, None, None

def get_recent_price(ticker):
    current_date = (datetime.now() - BDay(1)).strftime("%Y-%m-%d")  # Get the most recent business day
    response = requests_get_with_retry(f"https://api.polygon.io/v1/open-close/{ticker}/{current_date}?adjusted=true&apiKey={polygon_key}")
    data = response.json() if response else None
    if data and 'close' in data:
        recent_price = data['close']
    else:
        recent_price = None
    return recent_price

def save_to_db(date, ticker, historical_price_high, historical_price_low, historical_price_avg, recent_price, rsi, macd):
    query = """
        INSERT INTO sentiment_scores 
        (date, ticker, vader_sentiment, gpt_sentiment, gpt_response, historical_price_high, historical_price_low, historical_price_avg, aggregated_score, recent_price, rsi, macd) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    connection.cursor().execute(query, (date, ticker, None, None, None, historical_price_high, historical_price_low, historical_price_avg, None, recent_price, rsi, macd))
    connection.commit()  # commit right after inserting data for a ticker

def main():
    # Load tickers
    df = pd.read_csv('Tickers.csv')
    tickers = df.iloc[:, 2].tolist()

    for ticker in tickers:
        date = datetime.now().date().isoformat()
        rsi = get_rsi(ticker)
        macd = get_macd(ticker)
        historical_price_high, historical_price_low, historical_price_avg = get_historical_price(ticker)
        recent_price = get_recent_price(ticker)
        
        save_to_db(date, ticker, historical_price_high, historical_price_low, historical_price_avg, recent_price, rsi, macd)

if __name__ == "__main__":
    main()
