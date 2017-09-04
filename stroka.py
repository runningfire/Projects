def Prov(arg1,arg2):
    if arg1 == arg2: 
        return  '1'
    if len(arg1) > len(arg2):
    	return  '2'
    elif arg2=='learn':
    	return  '3'
V=Prov('1', '1')
print(V)

