# config.py
import os

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
    DATABASE_NAME = 'database.sqlite'
    TICKERS_FILE = 'Tickers.csv'
