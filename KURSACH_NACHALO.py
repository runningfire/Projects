import os , xlrd , openpyxl
from os.path import join, getsize, exists
from xlrd import open_workbook
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def searching_xls_xlsd(enter):      
#Здесь поиск файлов Excel в заданной пользователем папке
	print('Ищу xl файлы...')
	slash = os.sep
	xlfileslist = []
	for root, dirs, files in os.walk(enter):
		for file in files:
			if (os.path.splitext(file)[1] == '.xls') or (os.path.splitext(file)[1] == '.xlsx'):
				path = os.path.join(root, file)
				path = str(path)
				xlfileslist.append(path)
	print(xlfileslist[0])
	return xlfileslist

def open_parsing_xls_xlsx(path):
	#Открытие и считывание нужных для обработки данных из каждого отделього файла
	print('Открываю файл...')
	Isp = []
	Ins = []
	Irz = []
	file = openpyxl.load_workbook(path)
	res = len(file.sheetnames) 
	file = xlrd.open_workbook(path)
	print('Считываю данные...')
	for k in range(res):
		sheet = file.sheet_by_index(k)
		for i in range(sheet.ncols):
			data = sheet.cell_value(0,i)
			if data == 'Iсоп. , A' or data == 'Iсопр. , A' or data == 'Iсоп, A' or data == 'Iсопр, A':
				for j in range(sheet.nrows):
					Isp.append(sheet.cell_value(j,i))
			if data == 'Iнас. , A' or data == 'Iнасыщ. , A' or data == 'Iнас, A' or data == 'Iнасыщ, A':
				for j in range(sheet.nrows):
					Ins.append(sheet.cell_value(j,i))
			if data == 'Iразр. , A' or data ==  'Iраз. , A' or data == 'Iраз, A' or data == 'Iразр, A':
				for j in range(sheet.nrows):
					Irz.append(sheet.cell_value(j,i))			 						
	return Isp , Ins , Irz 	

def plot_graphs(x,y,text,flag,xs,ys):
	#Математическая обработка данных из файлов и построение графиков
	print('Строю эксперементальные зависимости...')
	if (type(x[0]) is str):
		xs = x.pop(0)
	if (type(y[0]) is str) :	
		ys = y.pop(0)
	plt.figure(flag)
	x = np.array(x)
	y = np.array(y)
	print(x,y)
	fig = plt.plot(x, y, '.')
	plt.xlabel(xs)
	plt.ylabel(ys)
	plt.title(text)
	return xs , ys





if __name__ == '__main__':
	#Обработка некоторых исключений
	enter = input('Введите путь к папке ')
	if not os.path.exists(enter):
		print('Указанного пути не существует')
		exit(0)
	xlfileslist = searching_xls_xlsd(enter)
	if xlfileslist == []:
		print('В этой папке не найдены xl файлы')
		exit(0)
	i = 0	
	for path in xlfileslist:
		#Выполнение всех функций
		uspic =  open_parsing_xls_xlsx(path)
		if uspic[0] == [] or uspic[1] == [] or uspic[2] == []:
			print('Файл пустой или в нём нет необходимых параметров')
			exit(0)
		for data in uspic:
			if data[0] == 'Iсоп. , A' or data[0] == 'Iсопр. , A' or data[0] == 'Iсоп, A' or data[0] == 'Iсопр, A':
				Isp = data
			if data[0] == 'Iнас. , A' or data[0] == 'Iнасыщ. , A' or data[0] == 'Iнас, A' or data[0] == 'Iнасыщ, A':
				Ins = data
			if  data[0] == 'Iразр. , A' or data[0] ==  'Iраз. , A' or data[0] == 'Iраз, A' or data[0] == 'Iразр, A':
				Irz = data		
		xs,xy = plot_graphs(Isp,Ins,'Зависимость тока насыщения от тока в соленоиде', 1+3*i,None,None)
		plot_graphs(Isp,Irz,'Зависимость тока разряда от тока в соленоиде', 2+3*i,xs,xy)
		i = i + 1
		#Показ зависимостей через адаптированную среду
	plt.show()
					

					

