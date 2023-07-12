import pandas as pd                        
from pytrends.request import TrendReq
from fpdf import FPDF
import sys

#----------------Write the result to a text file first---------------
def getAnalysis():

    sys.stdout = open('/Users/haoxuanxu/Documents/Baynovation-Intern-Task1/Analysis.txt', 'w')
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['Taylor Swift'])
    df = pytrend.interest_by_region()
    df.head(10)
    print(df)

getAnalysis()