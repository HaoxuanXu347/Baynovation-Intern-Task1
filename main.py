import bs4
import requests
from rake_nltk import Rake, Metric
from pytrends.request import TrendReq
from flask import Flask, request, render_template
import datetime
import re
import time
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential

app = Flask(__name__)

def extract_keywords(url):
    Keywords = [] # The extracted Keywords from the given website 
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    r = Rake(language='english',
             ranking_metric=Metric.WORD_DEGREE, 
             include_repeated_phrases=False,
             min_length=1, max_length=2)

    r.extract_keywords_from_text(soup.body.get_text(' ', strip=True))

    # Extract at maximum of 3 keywords
    for rating, keyword in r.get_ranked_phrases_with_scores():
        if len(Keywords) == 3:
            break
        if rating > 8:
            Keywords.append(keyword) 
        
    Keywords = [re.sub(r'[^a-zA-Z]', '', keyword) for keyword in Keywords] # Get rid of non-letter characters

    return Keywords

# Initialize a cache with a time-to-live (TTL) of 60 seconds
cache = TTLCache(maxsize=100, ttl=60)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_google_trends_data(keyword):
    # Check if the data is in the cache
    if keyword in cache:
        return cache[keyword]

    # Create a pytrends object
    pytrends = TrendReq(hl='en-US', tz=360)

    # Get the interest over time data for the provided keyword using TrendReq
    DATE_INTERVAL = f"{(datetime.date.today() - datetime.timedelta(days=30)).isoformat()} {(datetime.date.today() - datetime.timedelta(days=1)).isoformat()}"
    pytrends.build_payload([keyword], cat=0, timeframe=DATE_INTERVAL, geo='US', gprop='')

    # Get the interest over time data as a Pandas DataFrame
    trends_data = pytrends.interest_over_time()

    # Store the data in the cache
    cache[keyword] = trends_data

    # Add a delay of 2 seconds between requests
    time.sleep(2)

    return trends_data

def get_related_images(keyword):
    # Create a pytrends object
    pytrends = TrendReq(hl='en-US', tz=360)

    # Get related queries for the keyword
    pytrends.build_payload([keyword], cat=0, timeframe='today 1-m', geo='US', gprop='')
    related_queries = pytrends.related_queries()

    # Get the related image for the keyword
    related_queries_top = related_queries[keyword]['top']
    related_image = related_queries_top['image_url'] if related_queries_top is not None else None

    return related_image

@app.route('/', methods=['GET', 'POST'])
def home():
    keywords = []
    trends_data = None
    related_image = None
    message = None

    if request.method == 'POST':
        url = request.form.get('url')
        keywords = extract_keywords(url)

        # Debugging statement: Print the extracted keywords
        print("Extracted Keywords:", keywords)

        if not keywords:
            message = "No relevant keywords found in the given URL. Please try again with a different URL."
        else:
            try:
                trends_data = fetch_google_trends_data(keywords[0])
                # Debugging statement: Print the trends_data
                print("Google Trends Data:", trends_data)

                if trends_data is None or trends_data.empty:
                    message = "No Google Trends data available for the entered keyword."
                else:
                    related_image = get_related_images(keywords[0])
            except Exception as e:
                message = "Error fetching Google Trends data. Please try again later."

    return render_template('home.html', keywords=keywords, trends_data=trends_data, related_image=related_image, message=message)
