import csv


answers = {'привет':'И тебе привет', 'как дела':'Лучше всех', 'пока':'Увидимся'}
with open('export.csv', 'w', encoding='cp1251') as f:
	writer=csv.writer(f, delimiter=' ')
	for k,v in answers.items():
		writer.writerow([k , v])

			