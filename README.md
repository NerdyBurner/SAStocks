Readme File: Stock Market Sentiment Analysis Script using Polygon.io and OPEN.ai CHAT-GPT 3.5-Turbo

Application Functional Summary

config.py: This script sets up the configuration for the project, including environment variables for the OpenAI and Polygon API keys, and the names of the SQLite database and the CSV file containing the stock tickers.

database.py: This script is used to interact with a SQLite database. It includes a Database class with methods for saving and retrieving articles and sentiment scores.

api.py: This script fetches stock tickers from a CSV file and retrieves news related to those tickers from the Polygon.io API.

sentiment_analysis.py: This script performs sentiment analysis on the news articles fetched by the api.py script. It uses either the VADER sentiment analysis tool from NLTK or the OpenAI API to analyze the sentiment of the articles.

These scripts work together to fetch news related to a list of stock tickers, perform sentiment analysis on these news articles, and store both the articles and the sentiment scores in a SQLite database. The sentiment analysis can be performed by either NLTK's VADER or OpenAI's GPT-3.5-turbo, depending on the requirements of the task. Configuration for the project, such as API keys and filenames, is managed by the config.py script.


Required or Suggested Programs
Python 3.6 or higher is required to run this application. You'll also need several Python libraries, including pandas, nltk, requests, sqlite3, openai, and retrying. You can install these libraries using pip:

Copy code
pip install pandas nltk requests sqlite3 openai retrying
API Keys and Websites
You'll need API keys for the following services:

OpenAI: You can get an API key by creating an account on the OpenAI website (https://www.openai.com/). The cost is $20 per month plus additional charges based on usage - You pay per token using the gpt-3.5-turbo rates (subject to change, check open.ai)

Polygon.io: You can get an API key by creating an account on the Polygon.io website (https://polygon.io/). The cost is $30 per month.

Areas for Improvement
Code is currently being optimized - thanks to all involved
Model can be tuned with additional inputs and prompt clarification
Offline model to be generated
Gpt-4 analysis to be considered
Further improvements TBD - You are welcome to contribute!

Remember to always keep your API keys secure and never share them publicly.
