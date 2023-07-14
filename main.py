import bs4, requests
from rake_nltk import Rake
from rake_nltk import Metric, Rake
from requests_html import HTMLSession
from pytrends.request import TrendReq
from flask import Flask, request, render_template, Response
import pdfkit


#---------Task Assignment - Extracting Keywords and Analyzing Google Trends Data------

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

    link = ''
    Keywords = []
    if request.method == 'POST':
        url = request.form.get('url')
        link = url
        
        response = requests.get(link,headers={'User-Agent': 'Mozilla/5.0'})
        soup = bs4.BeautifulSoup(response.text,'lxml')
        r = Rake(language='english',
             ranking_metric=Metric.WORD_DEGREE, 
             include_repeated_phrases=False,
             min_length=2, max_length=4)

        r.extract_keywords_from_text(soup.body.get_text(' ', strip=True))

        for rating, keyword in r.get_ranked_phrases_with_scores():
            if len(Keywords) == 6:
                break
            if rating > 8:
                Keywords.append(keyword)

        
    return render_template('home.html', Keywords = Keywords)











   
    
        


