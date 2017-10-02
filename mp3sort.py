import os
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
from os.path import join, getsize, exists
import shutil


def searching_mp3(enter):
	#slash = os.sep
	mp3fileslist = []
	for root, dirs, files in os.walk(enter):
		for file in files:
			if os.path.splitext(file)[1] == '.mp3':
				path = os.path.join(root, file)
				mp3fileslist.append({'Filename':path, 'mp3tags':None})
	return mp3fileslist


def getting_tags(mp3fileslist):           
	#try:		    	
	for mp3dicts in mp3fileslist:
		mp3object = MP3File(mp3dicts['Filename'])
		mp3object.set_version(VERSION_2)
		mp3dicts['mp3tags'] = mp3object.get_tags()
	#except KeyError:
		#pass					   
	return mp3fileslist

def creator_cleaner(user_enter):
	slash = os.sep
	if os.path.exists(user_enter):
		for root, dirs, files in os.walk(user_enter):
			for direct in dirs:
				shutil.rmtree(os.path.join(user_enter, direct))	

def sort_folder_mp3files(mp3fileslist,user_enter,tag):
	slash = os.sep
	os.chdir(user_enter)
	for mp3file in mp3fileslist:
		value = (mp3file['mp3tags'])[tag]
		path = os.path.join(user_enter ,value )
		pathfrom = mp3file['Filename']
		changedname = os.path.split(pathfrom)
		print(changedname[-1])
		pathto = os.path.join(path,('copy'+changedname[-1]))
		print(pathto)
		if not os.path.exists(path):
			os.mkdir(value)
			shutil.copyfile(pathfrom, pathto)
		else:
			shutil.copyfile(pathfrom, pathto)
				


		






#Каждый номер списка тега совпадает с номером списка из mp3шек
if __name__ == '__main__':
	enter = input('Введите путь к папкес неотсортированной музыкой')
	user_enter = input('Введите папку ,где вы хотите сортировать музыку')
	creator_cleaner(user_enter)
	mp3fileslist = searching_mp3(enter)
	dictsongtaglist = getting_tags(mp3fileslist)
	tag = input('Введите тэг')
	sort_folder_mp3files(dictsongtaglist,user_enter,tag)		


		





