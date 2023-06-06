#Build as of 6.5.23
import sqlite3
from config import Config
import datetime
from typing import List

class Database:
    def __init__(self):
        self.connection = sqlite3.connect(Config.DATABASE_NAME)
        self.create_tables()
        self.cursor = self.connection.cursor()

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT,
                source TEXT,
                ticker TEXT,
                timestamp DATETIME NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiments (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                score REAL NOT NULL,
                timestamp DATETIME NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_data (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                rsi REAL,
                macd REAL,
                historical_price_high REAL,
                historical_price_low REAL,
                historical_price_avg REAL,
                recent_price REAL,
                vader_score REAL,
                gpt3_score REAL,
                final_score REAL,
                timestamp DATETIME NOT NULL
            )
        ''')
        self.connection.commit()

    def save_article(self, article):
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO articles (title, summary, source, ticker, timestamp) 
                VALUES (?, ?, ?, ?, ?)
            ''', (article['title'], article['summary'], article.get('source'), article['ticker'], article['timestamp']))
            self.connection.commit()
        except Exception as e:
            print(f"Error saving article: {str(e)}")

    def save_sentiment(self, sentiment):
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO sentiments (ticker, score, timestamp) 
                VALUES (?, ?, ?)
            ''', (sentiment['ticker'], sentiment['score'], sentiment['timestamp']))
            self.connection.commit()
        except Exception as e:
            print(f"Error saving sentiment: {str(e)}")

    def save_financial_data(self, ticker: str, rsi: float, macd: float, prices: List[float], final_score: float):
        data = {
            'ticker': ticker,
            'rsi': rsi,
            'macd': macd,
            'close_price': prices[-1] if prices else None,
            'final_score': final_score,
            'date': datetime.date.today().isoformat(),
        }
        self.cursor.execute("""
            INSERT INTO financial_data (ticker, rsi, macd, close_price, final_score, date)
            VALUES (:ticker, :rsi, :macd, :close_price, :final_score, :date)
        """, data)
        self.connection.commit()

    # Rest of the methods (get_article, get_sentiment, get_all_articles, get_all_sentiments, get_financial_data) go here...
    def get_article(self, id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM articles WHERE id = ?', (id,))
        return cursor.fetchone()

    def get_sentiment(self, id):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM sentiments WHERE id = ?', (id,))
        return cursor.fetchone()

    def get_all_articles(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM articles')
        return cursor.fetchall()

    def get_all_sentiments(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM sentiments')
        return cursor.fetchall()

    def get_financial_data(self, ticker):
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM financial_data WHERE ticker = ?', (ticker,))
        return cursor.fetchone() 
    
    def fetch_financial_report(self):
        self.cursor.execute("""
            SELECT ticker, recent_price, rsi, macd, vader_score, gpt3_score, final_score
            FROM financial_data
            ORDER BY final_score DESC
        """)
        return self.cursor.fetchall()
