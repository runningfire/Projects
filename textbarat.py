import os

statinfo = os.stat('output.txt').st_size
file = open('output.txt', 'w')
text = ''
while len(text.encode()) < 140:
	file.write('21212')
	text = text + '21212'
