#Build as of 6.3.23
from dotenv import load_dotenv
from api import Api
from database import Database
from sentiment_analysis import SentimentAnalysis
from config import Config

load_dotenv()

def main():
    # Initialize the Api, Database, and SentimentAnalysis classes
    api = Api(Config.POLYGON_API_KEY, Config.TICKERS_FILE)
    database = Database(Config.DATABASE_NAME)
    sentiment_analysis = SentimentAnalysis(Config.OPENAI_API_KEY)

    # Fetch the list of tickers
    tickers = api.fetch_tickers()

    # Process tickers in batches of 25
    for i in range(0, len(tickers), 25):
        batch_tickers = tickers[i:i+25]

        for ticker in batch_tickers:
            try:
                # Fetch and save financial data
                rsi = api.fetch_rsi(ticker)
                macd = api.fetch_macd(ticker)
                prices = api.fetch_prices(ticker)
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

                # Placeholder for final score calculation
                final_score = None  # TODO: Replace with actual calculation

                # Save the final score
                # TODO: Implement method to save final score in the database

            except Exception as e:
                print(f"An error occurred while processing ticker {ticker}: {str(e)}")

if __name__ == "__main__":
    main()
