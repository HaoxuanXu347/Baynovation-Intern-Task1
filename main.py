import bs4
import requests
from rake_nltk import Rake, Metric
from pytrends.request import TrendReq
from flask import Flask, request, render_template
from tenacity import retry, stop_after_attempt, wait_exponential
import datetime
import re
import requests.exceptions
from urllib3.util.retry import Retry
from requests import Session 


app = Flask(__name__)

def extract_keywords(url):
    Keywords = [] # The extracted Keywords from the given website 
    response = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs4.BeautifulSoup(response.text,'lxml')
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
        
        Keywords = [re.sub(r'[^a-zA-Z]', '', keyword) for keyword in Keywords] #Get rid of non-letter characters

    return Keywords

import time
import traceback
from requests.adapters import HTTPAdapter
from requests.sessions import Session

# ...

def fetch_google_trends_data(keyword):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_google_trends_data_with_retry():
        DATE_INTERVAL = f"{(datetime.date.today() - datetime.timedelta(days=30)).isoformat()} {(datetime.date.today() - datetime.timedelta(days=1)).isoformat()}"

        # Create a session with a Retry adapter
        session = Session()
        retry = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Get the interest over time data for the provided keyword using TrendReq
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([keyword], cat=0, timeframe=DATE_INTERVAL, geo='US', gprop='')

        # Extract required cookies from the initial requests made by TrendReq
        cookies = session.cookies.get_dict()

        # Now set the cookies manually in pytrends
        pytrends.cookies.update(cookies)

        # Get the interest over time data as a Pandas DataFrame
        trends_data = pytrends.interest_over_time()

        return trends_data

    try:
        trends_data = get_google_trends_data_with_retry()
        if trends_data is not None:
            time.sleep(2)  # Add a delay of 2 seconds between requests
        return trends_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Google Trends data: {e}")
        return None
    except Exception as e:
        traceback.print_exc()  # Print the traceback for the unexpected error
        print(f"Unexpected error fetching Google Trends data: {e}")
        return None



def get_related_images(keyword):
    pytrends = TrendReq(hl='en-US', tz=360)  # Create a pytrends object

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
            trends_data = fetch_google_trends_data(keywords[0])
            # Debugging statement: Print the trends_data
            print("Google Trends Data:", trends_data)

            if trends_data is None or trends_data.empty:
                message = "No Google Trends data available for the entered keyword."
            else:
                related_image = get_related_images(keywords[0])

    return render_template('home.html', keywords=keywords, trends_data=trends_data, related_image=related_image, message=message)

