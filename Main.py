from api import Api
from sentiment_analysis import SentimentAnalysis
from database import Database

# Instantiate the classes
api = Api()
sentiment_analysis = SentimentAnalysis()
database = Database()

# Fetch the stock tickers
tickers = api.fetch_tickers()

# For each ticker, fetch the related news articles
for ticker in tickers:
    news = api.fetch_news(ticker)
    
    # For each news article, perform sentiment analysis
    for article in news:
        sentiment_score_vader = sentiment_analysis.analyze_vader(article['summary'])
        sentiment_score_openai = sentiment_analysis.analyze_openai(article['summary'])

        # Save the article and sentiment scores to the database
        database.save_article(article)
        database.save_sentiment({'ticker': ticker, 'score_vader': sentiment_score_vader, 'score_openai': sentiment_score_openai})
