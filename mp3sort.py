import os
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
from os.path import join, getsize, exists


def searching_mp3(enter):
	# slash = '\ '.strip(' ')
	slash = os.sep
	mp3fileslist = []
	for root, dirs, files in os.walk(enter):
		for file in files:
			if os.path.splitext(file)[1] == '.mp3':
				path = os.path.join(root, file)
				mp3fileslist.append(path)
	return mp3fileslist


def getting_tags(mp3fileslist,mp3tag):           
	taglist = []
	#try:		    	
	for mp3files in mp3fileslist:
		mp3object = MP3File(mp3files)
		mp3object.set_version(VERSION_2)
		taglist.append(mp3object.get_tags()[mp3tag])
	#except KeyError:
		#pass					   
	return taglist	


#Каждый номер списка тега совпадает с номером списка из mp3шек
if __name__ == '__main__':
	enter = input('Введите путь к папке')
	mp3fileslist = searching_mp3(enter)
	mp3tag = input('Введите тег')
	taglist = getting_tags(mp3fileslist,mp3tag)
	print(mp3fileslist , ' ' , taglist)