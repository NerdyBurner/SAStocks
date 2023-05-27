import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import openai
from config import Config
from typing import Any, Dict, List, Union

class ChatCompletionResponse:
    choices: List[Dict[str, Any]]

    def __init__(self, **kwargs):
        self.choices = kwargs.get('choices', [])

class SentimentAnalysis:
    def __init__(self):
        nltk.download('vader_lexicon')
        self.vader = SentimentIntensityAnalyzer()
        openai.api_key = Config.OPENAI_API_KEY

    def analyze_vader(self, text):
        scores = self.vader.polarity_scores(text)
        return scores['compound']

def analyze_openai(self, text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "This is a sentiment analysis task. Please categorize the following news article's sentiment as 'Good', 'Bad', or 'Unknown'."},
                {"role": "user", "content": text}
                ]
            )
        if 'choices' in response and len(response.choices) > 0: # type: ignore \
            # Pylance is confused by there not being a 'choices' list, or that the list is empty. \
            # Ignoring it for now and focusing on adding core functionality as template \
            return response.choices[0].message['content'] # type: ignore \
        else:
            return 'API returned no \'Choices\' or the list itself was empty.'
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 'Error'
