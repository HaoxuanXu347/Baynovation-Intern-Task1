from requests_html import HTMLSession
from rake_nltk import Rake


# Get keywords using rake_nltk and save all the keywords into a txt file called Keywords.txt
def getKeywords(URL, file):
    def extract_text(URL):
        s = HTMLSession()
        response = s.get(URL)
        return response.html.find('div#comp-l8dw6g1k__item1', first=True).text

    with open(file, 'w') as f:
        r = Rake()
        r.extract_keywords_from_text(extract_text(URL))
        for rating, keyword in r.get_ranked_phrases_with_scores():
            if rating > 5:
                f.write(keyword)
                f.write('\n')




   
