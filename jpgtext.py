from fpdf import FPDF

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