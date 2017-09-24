import csv


def Max_repeated_row(csvfile):
	with open(csvfile , 'r' , encoding='cp1251') as file:
		reader = csv.DictReader(file, delimiter=';')	
		spisstreet = []
		for row in reader:
			spisstreet.append(row['Street'])		
		maxi = spisstreet.count(spisstreet[1])	
		for street in spisstreet:
			currentmaxi = spisstreet.count(street)
			if (currentmaxi > maxi):
				maxi = currentmaxi
				text = street
	return text
User_input = input('Введите имя файла')
try:
	text = Max_repeated_row(User_input)
	print(text)
except FileNotFoundError:
	print('Такого файла нет')	





				


