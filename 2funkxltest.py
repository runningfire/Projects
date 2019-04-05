import os , xlrd, openpyxl
from os.path import join, getsize, exists
from xlrd import open_workbook

file = openpyxl.load_workbook('C:\projects\Книга1')
res = len(file.sheetnames)
print(res) 