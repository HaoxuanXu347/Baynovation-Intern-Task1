import pandas as pd                        
from pytrends.request import TrendReq
from fpdf import FPDF
import sys
import requests

# Write the result to a text file first

def getAnalysis():

    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['Taylor Swift'])
    df = pytrend.interest_by_region()
    df.head(10)
    
    with open('Analysis.txt', 'w') as f:
        f.write(df)


getAnalysis()