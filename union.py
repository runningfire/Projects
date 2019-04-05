from PyPDF2 import PdfFileReader,PdfFileWriter 


for i in range(1,13):
	output = PdfFileWriter() 
	input1 = PdfFileReader(open(("month" + str(i) + ".pdf") , "rb")) 
	page1 = input1.getPage(0) 
	watermark = PdfFileReader(open(("blog_calendar" + str(i) +".pdf") , "rb")) 
	page1.mergePage(watermark.getPage(0)) 
	output.addPage(page1) 
	outputStream = open(("result" + str(i) + ".pdf") , "wb") 
	output.write(outputStream) 
	outputStream.close() 