import os, random



def encodering():
	ifile = open('input.bin')
	stringi = ifile.read()
	ifile.close()
	vfile = open('output.bin','w')
	text = ''
	while (len(text.encode())) < 140:
		randomint = random.randint(1,9)
		text = text + str(randomint)
		vfile.write(str(randomint)) 
	vfile = open('output.bin')
	stringv = vfile.read()
	vfile.close()


def decodering(message,code):	
	try:
		dfile = open('corrupted.bin')
		rfile = open('restored.bin', 'w')
		string_r = dfile.read()
		if code == string_r:
			rfile.write(message)
		else:
			rfile = open('restored.bin', 'w')
			rfile.write('CANNOT BE RESTORED')		
	except (OSError):
		rfile = open('restored.bin', 'w')
		rfile.write('CANNOT BE RESTORED')
	finally:
		dfile.close()
		rfile.close()


if __name__ == '__main__':
	if  os.path.exists('corrupted.bin'):
		ifileforma = open('input.bin')
		stringi = ifileforma.read()
		ifileforma.close()
		vfileforma = open('output.bin')
		stringv = vfileforma.read()
		vfileforma.close()
		decodering(stringi,stringv)
	else:
		encodering()		








