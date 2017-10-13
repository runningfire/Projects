import os
import shutil
import urllib.request as urllib_request 
import urllib.parse as urllib_parse
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH
from os.path import join, getsize, exists


def searching_mp3(enter):
	slash = os.sep
	mp3fileslist = []
	for root, dirs, files in os.walk(enter):
		for file in files:
			if os.path.splitext(file)[1] == '.mp3':
				path = os.path.join(root, file)
				mp3fileslist.append({'Filename':path, 'mp3tags':None})
	return mp3fileslist


def getting_tags(mp3fileslist,tag):           		    	
	for mp3dicts in mp3fileslist:
		mp3object = MP3File(mp3dicts['Filename'])
		mp3object.set_version(VERSION_2)
		mp3dicts['mp3tags'] = mp3object.get_tags()
		print(mp3dicts['mp3tags'])
		musictags = list(mp3dicts['mp3tags'].keys())
		print(musictags)
		print(musictags.count(tag))
		if (musictags.count(tag) == 0) and (musictags != []) :
			mp3fileslist = None
		if mp3fileslist is not None:		
			try:
				mp3dicts['mp3tags'][tag]
			except KeyError:
				mp3object.set_version(VERSION_1)
				mp3dicts['mp3tags'] = mp3object.get_tags()
	return mp3fileslist

#Если папка ,куда пользователь хочет отсортировать музыку не существует ,то она создаётся.
def creator_cleaner(user_enter):
	slash = os.sep
	if os.path.exists(user_enter):
		for root, dirs, files in os.walk(user_enter):
			for direct in dirs:
				shutil.rmtree(os.path.join(user_enter, direct))	
	else:
		os.mkdir(user_enter)

				
def sort_folder_mp3files(mp3fileslist,user_enter,tag):
	slash = os.sep
	os.chdir(user_enter)
	for mp3file in mp3fileslist:
		value = mp3file['mp3tags'][tag]
		if value is None:
			value = 'Untitled'		
		value = value.replace('\x00', '')
		value = value.replace('/', ' ')
		value = value.replace(':', ' ')
		value = value.replace(' " '.strip(), ' ')
		value = value.replace('?', ' ')
		value = value.replace(slash , ' ')
		value = value.replace('<', ' ')
		value = value.replace('>', ' ')
		value = value.replace('<', ' ')
		print('0', value.encode("utf-8"))
		path = os.path.join(user_enter, value )
		print('1', '"%s"'%path)
		pathfrom = mp3file['Filename']
		changedname = os.path.split(pathfrom)
		print('2', changedname[-1])
		pathto = os.path.join(path.strip(), ('copy'+changedname[-1]))
		print('3', pathto)
		if not os.path.exists(path):
			os.mkdir(value)
			shutil.copyfile(pathfrom, pathto)
		else:
			shutil.copyfile(pathfrom, pathto)
				


		






#Каждый номер списка тега совпадает с номером списка из mp3шек
if __name__ == '__main__':
	enter = input('Введите путь к папке с неотсортированной музыкой')
	if not os.path.exists(enter):
		print('Указанного пути не существует')
		exit(0)
	user_enter = input('Введите папку ,где вы хотите сортировать музыку')
	creator_cleaner(user_enter)
	tag = input('Введите тэг')
	mp3fileslist = searching_mp3(enter)
	if mp3fileslist == []:
		print('В этой папке не найдены mp3 файлы')
		exit(0)
	dictsongtaglist = getting_tags(mp3fileslist,tag)
	if dictsongtaglist is not None:
		sort_folder_mp3files(dictsongtaglist,user_enter,tag)
	else:
		print('Запрашиваемого тега не существует')
		exit(0)			


		





