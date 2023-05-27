# Get required components
import pandas as pd
from pandas.tseries.offsets import BDay
import requests
from datetime import datetime, timedelta
from sqlite3 import dbapi2 as sqlite

# Load API keys from CSV
keys_df = pd.read_csv('api_keys.csv')
polygon_key = keys_df['polygon_key'].values[0]

# Polygon.io API setup
polygon_url = "https://api.polygon.io/v1/meta/symbols/{ticker}/news?perpage=50&page=1&apiKey=" + polygon_key

def load_tickers():
    df = pd.read_csv('Tickers.csv')
    tickers = df.iloc[:, 2].tolist()
    return tickers

# Database connection for news articles
news_database_filename = 'news_articles.db'
news_connection = sqlite.connect(news_database_filename)

# Extend table schema to accommodate more details
news_connection.cursor().execute('''
    CREATE TABLE IF NOT EXISTS news_articles
    (
        date text,
        ticker text,
        title text,
        description text,
        article_url text,
        author text,
        keywords text,
        publisher text,
        image_url text,
        amp_url text
    )
''')

def save_news_to_db(date, ticker, title, description, article_url, author, keywords, publisher, image_url, amp_url):
    # Check if article already exists in the database
    cursor = news_connection.cursor()
    cursor.execute("SELECT * FROM news_articles WHERE article_url = ?", (article_url,))
    data = cursor.fetchone()
    if data is None:
        # Insert if not already present
        query = """
            INSERT INTO news_articles 
            (date, ticker, title, description, article_url, author, keywords, publisher, image_url, amp_url) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (date, ticker, title, description, article_url, author, keywords, publisher, image_url, amp_url))
        news_connection.commit()
    else:
        print(f"Article '{title}' already exists in database.")
def process_api_response(api_response, ticker):
    if api_response.get('status') != "OK":
        print(f"Error: {api_response.get('status')} - {api_response.get('error')}")
        return
    for result in api_response['results']:
        date = result['published_utc']
        title = result['title']
        description = result['description']
        article_url = result['article_url']
        author = result['author']
        keywords = ", ".join(result['keywords'])
        publisher = result['publisher']['name']
        image_url = result['image_url']
        amp_url = result['amp_url']
        save_news_to_db(date, ticker, title, description, article_url, author, keywords, publisher, image_url, amp_url)


print("Starting news pull from 5/1/23")

# Load the tickers
tickers = load_tickers()

# Download news articles for all tickers
print("Importing and Filtering News from Polygon.io for all tickers")
processed_tickers = []  # You might have this defined somewhere else
for i, ticker in enumerate(tickers, start=1):
    if ticker in processed_tickers:
        continue  # Skip tickers that have been processed already
    print(f"\nImporting news for ticker #{i}: {ticker}")

    # Execute the request, get the response and process it
    try:
        api_response = requests.get(polygon_url.format(ticker=ticker)).json()
        process_api_response(api_response, ticker)
    except Exception as e:
        print(f"An error occurred while processing {ticker}: {e}")
        continue

    print(f"Finished importing and filtering news for {ticker}")

print("News Capture Completed - Database Prepared")

# Close the database connection when you're done
news_connection.close()
