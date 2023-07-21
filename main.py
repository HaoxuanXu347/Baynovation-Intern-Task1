import bs4
import requests
from rake_nltk import Rake, Metric
from pytrends.request import TrendReq
from flask import Flask, request, render_template
import datetime
import re
import time

app = Flask(__name__)

def extract_keywords(url):
    Keywords = [] # The extracted Keywords from the given website 
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    r = Rake(language='english',
             ranking_metric=Metric.WORD_DEGREE, 
             include_repeated_phrases=False,
             min_length=1, max_length=3)

    r.extract_keywords_from_text(soup.body.get_text(' ', strip=True))

    # Extract at maximum of 3 keywords
    for rating, keyword in r.get_ranked_phrases_with_scores():
        if len(Keywords) == 6:
            break
        if rating > 8:
            Keywords.append(keyword) 
        
    Keywords = [re.sub(r'[^a-zA-Z]', '', keyword) for keyword in Keywords] # Get rid of non-letter characters

    return Keywords

def fetch_google_trends_data(keyword):
    # Create a pytrends object
    pytrends = TrendReq(hl='en-US', tz=360)

    # Get the interest over time data for the provided keyword using TrendReq
    DATE_INTERVAL = f"{(datetime.date.today() - datetime.timedelta(days=30)).isoformat()} {(datetime.date.today() - datetime.timedelta(days=1)).isoformat()}"
    pytrends.build_payload([keyword], cat=0, timeframe=DATE_INTERVAL, geo='US', gprop='')

    # Get the interest over time data as a Pandas DataFrame
    trends_data = pytrends.interest_over_time()

    time.sleep(2)

    # Get the related topics for the provided keyword
    related_topics_data = pytrends.related_topics()

    # Add a delay of 2 seconds between requests
    time.sleep(2)

    return trends_data, related_topics_data

@app.route('/', methods=['GET', 'POST'])
def home():
    keywords = []
    trends_data = None
    related_topics_data = None
    message = None

    if request.method == 'POST':
        url = request.form.get('url')
        keywords = extract_keywords(url) 

        if not keywords:
            message = "No relevant keywords found in the given URL. Please try again with a different URL."
        else:
            try:
                trends_data, related_topics_data = fetch_google_trends_data(keywords[0])
                # Debugging statements: Print the trends_data and related_topics_data
                print("Google Trends Data:", trends_data)
                print("Related Topics Data:", related_topics_data)

                if trends_data is None or trends_data.empty:
                    message = "No Google Trends data available for the entered keyword."
            except Exception as e:
                message = "Error fetching Google Trends data. Please try again later."

    return render_template('home.html', keywords=keywords, trends_data=trends_data, related_topics_data=related_topics_data, message=message)


