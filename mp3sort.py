import os
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
from os.path import join, getsize,exists


def Searching_Mp3(enter):
	slash = '\ '.strip(' ')
	mp3spic = []
	for root, dirs, files in os.walk(enter):
		for file in files:
			name_format = file.split('.')
			if name_format[-1]=='mp3':
				path = root + slash + file
				mp3spic.append(path)
	return mp3spic

def Editing_tags(mp3spic,tag):
	tagspic = []
	#try:		    	
	for music in mp3spic:
		mp3 = MP3File(music)
		mp3.set_version(VERSION_2)
		tagspic.append(mp3.get_tags()[tag])
	#except KeyError:
		#pass					   
	return tagspic	

enter = input('Введите путь к папке')
mp3spic = Searching_Mp3(enter)
tag = input('Введите тег')
tagspic = Editing_tags(mp3spic,tag)
print(mp3spic , ' ' , tagspic)
				

				

