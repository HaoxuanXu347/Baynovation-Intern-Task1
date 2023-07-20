import bs4, requests
from rake_nltk import Rake
from rake_nltk import Metric, Rake
from requests_html import HTMLSession
from pytrends.request import TrendReq
from flask import Flask, request, render_template, Response, jsonify
import pdfkit
import pandas as pd
import pytrends
import time
import base64
from io import BytesIO

#---------Task Assignment - Extracting Keywords and Analyzing Google Trends Data------

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

    link = ''
    Keywords = [] # The extracted Keywords from the given website
    if request.method == 'POST':
        url = request.form.get('url') # The URL given by the user
        link = url
        
        response = requests.get(link,headers={'User-Agent': 'Mozilla/5.0'})
        soup = bs4.BeautifulSoup(response.text,'lxml')
        r = Rake(language='english',
             ranking_metric=Metric.WORD_DEGREE, 
             include_repeated_phrases=False,
             min_length=2, max_length=4)

        r.extract_keywords_from_text(soup.body.get_text(' ', strip=True))

        # Extract at maximum of 6 keywords
        for rating, keyword in r.get_ranked_phrases_with_scores():
            if len(Keywords) == 3:
                break
            if rating > 8:
                Keywords.append(keyword)  

    #-----------------Get Google Trend Data---------------#
        requests_args = {
            'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            }
        }
        pytrend = TrendReq(requests_args=requests_args)
        DATE_INTERVAL='2020-01-01 2020-05-01'

        try:
            pytrend.build_payload(kw_list={Keywords[0]}, timeframe=DATE_INTERVAL, geo='US')
            trends_data = pytrend.interest_over_time()
            trends_data.to_dict()
            time.sleep(2)    

            return render_template('home.html', Keywords = Keywords, trends_data = trends_data)
        except requests.Timeout as err:
            print({"message": err.message}) 
                
    return render_template('home.html', Keywords = Keywords)












