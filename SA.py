# Importing required tools
import pandas as pd
from pandas.tseries.offsets import BDay
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import date, datetime, timedelta
import openai
from sqlite3 import dbapi2 as sqlite
from retrying import retry
import time
from datetime import datetime
import traceback

# Load API keys from CSV
keys_df = pd.read_csv('api_keys.csv')
openai_key = keys_df['openai_key'].values[0]
polygon_key = keys_df['polygon_key'].values[0]

# OpenAI and Polygon.io API setup
openai.api_key = openai_key
polygon_url = "https://api.polygon.io/v1/meta/symbols/{ticker}/news?perpage=50&page=1&apiKey=" + polygon_key

def load_tickers():
    df = pd.read_csv('Tickers.csv')
    tickers = df.iloc[:, 2].tolist()
    return tickers

# Database connection
database_filename = 'sentiment_scores.db'
connection = sqlite.connect(database_filename)

connection.cursor().execute('''
    CREATE TABLE IF NOT EXISTS sentiment_scores
    (date text, ticker text, vader_sentiment text, gpt_sentiment text, gpt_response text,
        historical_price_high real, historical_price_low real, historical_price_avg real, aggregated_score real,
        recent_price real, rsi real, macd real)
''')

# Vader Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

def get_latest_date_in_db():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(date) FROM sentiment_scores")
    result = cursor.fetchone()
    if result[0] is not None:
        return datetime.strptime(result[0], '%Y-%m-%d').date()
    else:
        return None

@retry(stop_max_attempt_number=7, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def requests_get_with_retry(url):
    response = requests.get(url)
    response.raise_for_status()  # Raises stored HTTPError, if one occurred
    return response

def get_stock_news(ticker):
    try:
        url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}&apiKey={polygon_key}"
        response = requests.get(url)
        data = response.json()

        if 'status' in data and data['status'] == "OK":
            return data['results']
        else:
            return []
    except Exception as e:
        print(f"Error getting stock news for {ticker}: {e}")
        return []

def get_rsi(ticker, polygon_key):
    rsi_url = f"https://api.polygon.io/v1/indicators/rsi/{ticker}?apiKey={polygon_key}"
    rsi_response = requests_get_with_retry(rsi_url)
    if rsi_response.status_code == 200:
        rsi_data = rsi_response.json()['results']['values']
        return rsi_data if rsi_data else None
    else:
        print(f"Error in get_rsi() for ticker {ticker}: {rsi_response.status_code}")
        return None

def get_macd(ticker, polygon_key):
    macd_url = f"https://api.polygon.io/v1/indicators/macd/{ticker}?apiKey={polygon_key}"
    macd_response = requests_get_with_retry(macd_url)
    if macd_response.status_code == 200:
        macd_data = macd_response.json()['results']['values']
        return macd_data if macd_data else None
    else:
        print(f"Error in get_macd() for ticker {ticker}: {macd_response.status_code}")
        return None

def filter_articles(articles):
    unwanted_phrases = ["stock gain", "stock loss"]
    seen_titles = set()

    filtered_articles = []
    for article in articles:
        if any(phrase in article['title'].lower() for phrase in unwanted_phrases):
            continue  # Skip this article if an unwanted phrase is in the title

        if article['title'] in seen_titles:
            continue  # Skip this article if we've already seen this title

        # If the article passed the above checks, add it to the filtered list and the seen titles
        filtered_articles.append(article)
        seen_titles.add(article['title'])

    return filtered_articles

def vader_sentiment_analysis(text):
    sentiment_score = analyzer.polarity_scores(text)
    compound_score = sentiment_score['compound']
    if compound_score >= 0.05:
        return "Good"
    elif compound_score <= -0.05:
        return "Bad"
    else:
        return "Neutral"

def gpt_sentiment_analysis(ticker, text, max_retries=3, retry_delay=1.0):
    for i in range(max_retries):
        try:
            prompt = f"Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert with stock recommendation experience. Answer 'Good' if good news, 'Bad' if bad news, or 'UNKNOWN' if uncertain in the first line. Then elaborate with one short and concise sentence on the next line. Is this information {text} good or bad for the stock price of {ticker} in the short term?"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial assistant with stock picking experience."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300)
                
            full_response = response['choices'][0]['message']['content'].strip()
            sentiment = full_response.split('\n')[0].strip().upper()

            if sentiment not in ['GOOD', 'BAD', 'UNKNOWN']:
                sentiment = 'UNKNOWN'

            return sentiment, full_response

        except Exception as e:
            print(f"Error during GPT sentiment analysis: {e}")
            if i < max_retries - 1:  # if not the last retry attempt
                time.sleep(retry_delay)  # wait before next retry
            else:
                return 'Error', 'Error'  # return Error after all retry attempts failed

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

def save_to_db(date, ticker, vader_sentiment, gpt_sentiment, gpt_response, historical_price_high, historical_price_low, historical_price_avg, aggregated_score, recent_price, rsi, macd):
    query = """
        INSERT INTO sentiment_scores 
        (date, ticker, vader_sentiment, gpt_sentiment, gpt_response, historical_price_high, historical_price_low, historical_price_avg, aggregated_score, recent_price, rsi, macd) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    connection.cursor().execute(query, (date, ticker, vader_sentiment, gpt_sentiment, gpt_response, historical_price_high, historical_price_low, historical_price_avg, aggregated_score, recent_price, rsi, macd))
    connection.commit()

def print_report(report_data):
    print("Here is your report:")
    for ticker, score in report_data:
        print(f"{ticker}: {score}")
    # Write the report to a file
    with open('report.txt', 'w') as f:
        f.write("Report:\n")
        for ticker, score in report_data:
            f.write(f"{ticker}: {score}\n")
    print("Report written to report.txt")

def calculate_aggregated_score(vader_sentiment, gpt_sentiment, historical_price_low, historical_price_high, recent_price, news_volume, rsi, macd):
    vader_score = {"Good": 1, "Neutral": 0, "Bad": -1}[vader_sentiment]
    gpt_score = {"Good": 1, "UNKNOWN": 0 , "Bad": -1}[gpt_sentiment]
    
    price_score = 0
    if recent_price < historical_price_low:
        price_score = -1
    elif recent_price > historical_price_high:
        price_score = 1

    news_volume_score = 0
    if news_volume > 10:
        news_volume_score = 1
    elif news_volume < 5:
        news_volume_score = -1

    rsi_score = 0
    if rsi < 30:
        rsi_score = -1
    elif rsi > 70:
        rsi_score = 1

    macd_score = 0
    if macd < 0:
        macd_score = -1
    elif macd > 0:
        macd_score = 1

    aggregated_score = (vader_score + gpt_score + price_score + news_volume_score + rsi_score + macd_score) / 6

    return aggregated_score

def main():
    sentiment_scores = {"Good": 1, "Neutral": 0, "UNKNOWN": 0, "Bad": -1}

    try:
        # Load tickers
        print("Starting Analysis - Reading Tickers.csv")
        tickers = load_tickers()
        print(f"Loaded {len(tickers)} tickers.")

        if not tickers:
            print("No tickers found. Exiting.")
            return

        report_data = []

        for i, ticker in enumerate(tickers, start=1):
            print(f"\nProcessing ticker #{i}: {ticker}")

            # Get news articles
            print("Importing and Filtering News from Polygon.io")
            news = get_stock_news(ticker)
            print(f"Loaded and filtered {len(news)} news articles.")

            if not news:
                print(f"No news articles found for {ticker}. Skipping.")
                continue

            # Get RSI and MACD
            rsi_data = get_rsi(ticker, polygon_key)
            macd_data = get_macd(ticker, polygon_key)

            # Extract the most recent value
            rsi = rsi_data[0]['value'] if rsi_data else None
            macd = macd_data[0]['value'] if macd_data else None

            # Process news articles
            print("Conducting sentiment analysis and scoring")
            vader_total = 0
            gpt_total = 0
            articles_processed = 0
            for article in news:
                if 'description' not in article:
                    print(f"Article does not contain a description: {article}")
                    continue

                articles_processed += 1

                title = article['title']
                description = article['description']

                # Get sentiment
                vader_sentiment = vader_sentiment_analysis(title+description)
                gpt_sentiment, gpt_response = gpt_sentiment_analysis(title+description)

                # Update total sentiment scores
                vader_total += sentiment_scores[vader_sentiment]
                gpt_total += sentiment_scores[gpt_sentiment]

                # Print result of news article
                print(f"Processing article: Vader: {vader_sentiment}, GPT: {gpt_sentiment}, GPT Comment: {gpt_response}")

            # Skip ticker if no articles were processed
            if articles_processed == 0:
                print(f"No articles were processed for {ticker}. Skipping.")
                continue

            # Get recent price
            recent_price = get_recent_price(ticker)

            # Calculate scores and save to database
            historical_price_high, historical_price_low, historical_price_avg = get_historical_price(ticker)

            # Now that all articles have been processed, calculate the aggregated score
            aggregated_score = calculate_aggregated_score(vader_total, gpt_total, historical_price_low, historical_price_high, recent_price, len(news), rsi, macd)

            # Print calculated final scoring
            print(f"Aggregated Score for {ticker}: {aggregated_score}")

            # Add the ticker and score to the report data
            report_data.append((ticker, aggregated_score))

            print(f"Finished Processing Ticker #{i}: {ticker}")

        # Sort the report data by score in descending order
        report_data.sort(key=lambda x: x[1], reverse=True)

        # Print and write the report
        print_report(report_data)

    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
