from fpdf import FPDF

# ----------------Convert the result to a PDF file-----------------
def convertPDF():   
    pdf = FPDF()  
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
 
    f = open('Analysis.txt', "r")
    for x in f:
        pdf.cell(200, 10, txt = x, ln = 1, align = 'C')
    pdf.output("Result.pdf")   

convertPDF()