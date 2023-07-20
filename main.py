import bs4
import requests
from rake_nltk import Rake, Metric
from pytrends.request import TrendReq
from flask import Flask, request, render_template
from tenacity import retry, stop_after_attempt, wait_exponential

app = Flask(__name__)

def extract_keywords(url):
    Keywords = [] # The extracted Keywords from the given website 
    response = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs4.BeautifulSoup(response.text,'lxml')
    r = Rake(language='english',
             ranking_metric=Metric.WORD_DEGREE, 
             include_repeated_phrases=False,
             min_length=1, max_length=3)

    r.extract_keywords_from_text(soup.body.get_text(' ', strip=True))

        # Extract at maximum of 6 keywords
    for rating, keyword in r.get_ranked_phrases_with_scores():
        if len(Keywords) == 3:
            break
        if rating > 8:
            Keywords.append(keyword) 
    return Keywords

def fetch_google_trends_data(keyword):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_google_trends_data_with_retry():
        pytrends = TrendReq(hl='en-US', tz=360)  # Create a pytrends object

        # Get the interest over time data for the provided keyword
        pytrends.build_payload([keyword], cat=0, timeframe='today 1-m', geo='US', gprop='')

        # Get the interest over time data as a Pandas DataFrame
        trends_data = pytrends.interest_over_time()

        return trends_data

    try:
        return get_google_trends_data_with_retry()
    except Exception as e:
        print(f"Error fetching Google Trends data: {e}")
        return None

def get_related_images(keyword):
    pytrends = TrendReq(hl='en-US', tz=360)  # Create a pytrends object

    # Get related queries (topics) for the keyword
    pytrends.build_payload([keyword], cat=0, timeframe='today 1-m', geo='US', gprop='')
    related_queries = pytrends.related_queries()

    # Get the top related image for the keyword
    related_image = related_queries[keyword]['top']['image_url']
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

        if keywords:
            trends_data = fetch_google_trends_data(keywords[0])
            if trends_data is None or trends_data.empty:
                message = "No Google Trends data available for the entered keyword."
            else:
                related_image = get_related_images(keywords[0])

    return render_template('home.html', keywords=keywords, trends_data=trends_data, related_image=related_image, message=message)
