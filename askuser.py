import answers
def ask_user(txt):
	try:
		while True:
			print(answers[txt])
			if txt=='пока':
				break
	except KeyError:
		print('Я такого не знаю') 						
	try:
		while True:
			text=input('Как дела?')
			if text=='Хорошо':
				break
	except KeyboardInterrupt:
		print('Ну пока')
user_text = input('Скажи что-нибудь')		
ask_user(user_text)				