dict = {'len': ' 45', 'Veg': '35'}
a = dict['len']
b = dict['Veg']
c = int(a)*100
d = int(b)*100
str(c)
str(d)
dict['len']= c
dict['Veg']= d
print(dict)