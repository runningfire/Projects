import csv
answers = {'привет':'И тебе привет', 'как дела':'Лучше всех', 'пока':'Увидимся'}
with open('export.csv', 'w', encoding='utf-8') as f:
	writer = csv.DictWriter(f, answers, delimeter=';')
	writer.writeheader()
	writer.writerows(answers)

