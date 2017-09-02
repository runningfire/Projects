def get_answer(q):
	answers = {'привет':'И тебе привет', 'как дела':'Лучше всех', 'пока':'Увидимся'}
	return answers[q].lower()
print(get_answer('привет'))	