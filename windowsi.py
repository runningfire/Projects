w1=[0,0,0,0]
w2=[0,0,0,0]
w3=[0,0,0,0]
w4=[0,0,0,0]
surf=[0,0,0,0]
for i in range(4):
	w1[i]=input('Введите координату для окна 1,начиная с x0')
for i in range(4):
	w2[i]=input('Введите координату для окна 2,начиная с x0')
for i in range(4):
	w3[i]=input('Введите координату для окна 3,начиная с x0')
for i in range(4):
	w4[i]=input('Введите координату для окна 4,начиная с x0')
for i in range(4):
	surf[i]=input('Введите номер слоя для каждого окна ,начиная с 1')
xm=input('Введите координату x указателя')
ym=input('Введите координату y указателя')
if ((xm <= w1[1]) and (xm >= w1[0]) and (ym <= w1[3]) and (ym >= w1[2])):
	 m=surf[0] 
	 surf[0]='1'
	 for i in range(4):
	 	if i != 0:
	 		if surf[i]=='1':
	 			surf[i]=m
	 print('окно 1')
elif ((xm <= w2[1]) and (xm >= w2[0]) and (ym <= w2[3]) and (ym >= w2[2])):
	 m=surf[1]
	 surf[1]='1'
	 for i in range(4):
	 	if i != 1:
	 		if surf[i]=='1':
	 			surf[i]=m
	 print('окно 2') 	 	      
elif ((xm <= w3[1]) and (xm >= w3[0]) and (ym <= w3[3]) and (ym >= w3[2])):
	 m=surf[2]
	 surf[2]='1'
	 for i in range(4):
	 	if i != 2:
	 		if surf[i]=='1':
	 			surf[i]=m
	 print('окно 3')
elif ((xm <= w4[1]) and (xm >= w4[0]) and (ym <= w4[3]) and (ym >= w4[2])):
	 m=surf[3] 
	 surf[3]='1'
	 for i in range(4):
	 	if i != 3:
	 		if surf[i]=='1':
	 			surf[i]=m
	 print('окно 4')
else:
	print('Координаты вне окон')
print('Окна и слои')
print('1','2','3','4')
print(surf)		 					