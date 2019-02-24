from reportlab.lib import pagesizes 
from reportlab.pdfgen.canvas import Canvas 
import calendar, time, datetime 
from math import floor 
from PyPDF2 import PdfFileReader,PdfFileWriter,PdfFileMerger 
from fpdf import FPDF

NOW = datetime.datetime.now() 
SIZE = pagesizes.landscape(pagesizes.A4) 

class NoCanvasError(Exception): pass 

def nonzero(row): 
    return len([x for x in row if x!=0]) 

def createCalendar(month, year=NOW.year, canvas=None, filename=None,  
        size=SIZE): 

    if type(month) == type(''): 
     month = time.strptime(month, "%b")[1] 
    if canvas is None and filename is not None: 
     canvas = Canvas(filename, size) 
    elif canvas is None and filename is None: 
     raise NoCanvasError 
    monthname = time.strftime("%B", time.strptime(str(month), "%m")) 
    cal = calendar.monthcalendar(year, month) 

    width, height = size 

    title = monthname + ' ' + str(year) 
    canvas.drawCentredString(width/2, height - 27, title) 
    height = height - 40 

    wmar, hmar = 0/50, 0/50 

    width, height = width - (2*wmar), height - (2*hmar) 
    rows, cols = len(cal), 7 
    lastweek = nonzero(cal[-1]) 
    firstweek = nonzero(cal[0]) 
    weeks = len(cal) 
    rowheight = floor(height/rows) 
    boxwidth = floor(width/7) 

    canvas.line(wmar, hmar, wmar+(boxwidth*lastweek), hmar ) 
    for row in range(1, len(cal[1:-1]) + 1): 
     y = hmar + (row * rowheight) 
     canvas.line(wmar, y, wmar + (boxwidth * 7), y) 
    y = hmar + ((rows-1) * rowheight) 
    canvas.line(wmar, y, wmar + (boxwidth * 7), y)  
    startx = wmar + (boxwidth * (7-firstweek)) 
    endx = startx + (boxwidth * firstweek) 
    y = y + rowheight 
    canvas.line(startx, y, endx, y, ) 

     
    for col in range(8):  
        last, first = 1, 1 
        if col <= lastweek: last = 0 
        if col >= 7 - firstweek: first = 0 
        x = wmar + (col * boxwidth) 
        starty = hmar + (last * rowheight) 
        endy = hmar + (rows * rowheight) - (first * rowheight) 
        canvas.line(x, starty, x, endy, ) 

    x = wmar + 6 
    y = hmar + (rows * rowheight) - 15 
    for week in cal: 
     for day in week: 
      if day: 
       canvas.drawString(x, y, str(day), 2) 
      x = x + boxwidth 
     y = y - rowheight 
     x = wmar + 6 

    canvas.showPage() 

    return canvas 

def pict_pdf():
    for i in range(1,13):
        if (i==1) or (i==3) or (i==4) or (i==6) or (i==8):
            image_path = 'j' + str(i) + '.png'
        else:
            image_path = 'j' + str(i) + '.jpg'       
        pdf = FPDF(orientation = 'L')
        pdf.add_page()
        pdf.image(image_path, x=50 , y=40 , w=190 , h=190)
        pdf.set_font("Arial", size=12)
        pdf.cell(530, 2, txt="from python with love...", ln=1, align="C")
        pdf.ln(85)
        pdf.output("month" + str(i) + ".pdf")   

def unite():
    pdflist = []
    for i in range(1,13):
        output = PdfFileWriter() 
        input1 = PdfFileReader(open(("month" + str(i) + ".pdf") , "rb")) 
        page1 = input1.getPage(0) 
        watermark = PdfFileReader(open(("blog_calendar" + str(i) +".pdf") , "rb")) 
        page1.mergePage(watermark.getPage(0)) 
        output.addPage(page1)
        inp = "result" + str(i) + ".pdf"
        pdflist.append(inp) 
        outputStream = open((inp) , "wb") 
        output.write(outputStream) 
        outputStream.close()
    return pdflist  

def pdffilesunite(li):
    merger = PdfFileMerger()

    for pdf in li:
        merger.append(open(pdf, 'rb'))

    with open('result.pdf', 'wb') as fout:
        merger.write(fout)       




if __name__ == "__main__": 
    for i in range(1,13):
        c = createCalendar(i, 2019, filename=("blog_calendar" + str(i) + ".pdf")) 
        c.save()
    pict_pdf()
    pdfl = unite()
    print(pdfl)
    pdffilesunite(pdfl)


