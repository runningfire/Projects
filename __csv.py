import csv
import answers
with open('export.csv', 'w', encoding='utf-8') as f:
	writer = csv.DictWriter(f, answers1, delimeter=';')
	writer.writeheader()
	for answers1[q] in answers1:
		writer.writerow(answers1[q])

