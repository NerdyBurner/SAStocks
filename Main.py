from dotenv import load_dotenv
from api import Api
from database import Database
from sentiment_analysis import SentimentAnalysis
from config import Config
import logging
import csv

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

def main():
    # Initialize the Api, Database, and SentimentAnalysis classes
    api = Api()
    database = Database()
    sentiment_analysis = SentimentAnalysis(Config.OPENAI_API_KEY)

    # Define start_date and end_date
    start_date = '2023-05-29'
    end_date = '2023-06-05'  # Replace with your desired end date

    # Fetch the list of tickers from the CSV file
    with open(Config.TICKERS_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        tickers = [row[2] for row in reader]  # Get the ticker from the third column

    # Process tickers in batches of 25
    for i in range(0, len(tickers), 25):

        for ticker in tickers:
            try:
                # Fetch and save financial data
                rsi = api.fetch_rsi(ticker)
                macd = api.fetch_macd(ticker)
                prices = api.fetch_prices(ticker, start_date, end_date)
                database.save_financial_data(ticker, rsi, macd, prices)

                # Initialize sentiment score counters
                vader_score_sum = 0
                openai_score_sum = 0
                num_articles = 0

                # Fetch news and perform sentiment analysis
                news_articles = api.fetch_news(ticker)
                for article in news_articles:
                    text = article['summary']
                    vader_score = sentiment_analysis.analyze_vader(text)
                    openai_score = sentiment_analysis.analyze_openai(text)

                    # Accumulate sentiment scores
                    vader_score_sum += vader_score
                    openai_score_sum += openai_score
                    num_articles += 1

                    # Save the sentiment scores
                    database.save_sentiment(ticker, vader_score, openai_score)

                # Calculate average sentiment scores
                vader_score_avg = vader_score_sum / num_articles if num_articles > 0 else 0
                openai_score_avg = openai_score_sum / num_articles if num_articles > 0 else 0

                # Calculate potential upside
                recent_price = prices[-1] if prices else 0
                historical_price_max = max(prices) if prices else 0
                potential_upside = historical_price_max - recent_price

                # Normalize potential_upside to -1 to 1 range
                potential_upside_normalized = (potential_upside - min(prices)) / (max(prices) - min(prices)) * 2 - 1 if prices else 0

                # Ensure non-zero and non-null values
                rsi = rsi if rsi and rsi != 0 else 1
                macd = macd if macd and macd != 0 else 1

                # Calculate final score
                final_score = round((vader_score_avg + openai_score_avg) * rsi * macd * potential_upside_normalized, 2)

                # Save the final score
                database.save_financial_data(ticker, rsi, macd, prices, final_score)
                
            except Exception as e:
                logging.error(f"An error occurred while processing ticker {ticker}: {str(e)}")

    # Fetch and print the report
    report = database.fetch_financial_report()
    print("Ticker, Recent Price, RSI, MACD, Vader Score, OpenAI Score, Final Score")
    for row in report:
        print(', '.join(str(x) for x in row))

if __name__ == "__main__":
    main()
