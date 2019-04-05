import os
import random


ish_file = open('input.bin')
string = ish_file.read()
ish_file.close()
vih_file = open('output.bin','w')
statinfo = os.stat(vih_file)
while statinfo.st_size < 140L:
	vih_file.write(str(random.randint(0, 1)) + " ")
vih_file = open('output.bin')
string1 = vih_file.read()
vih_file.close()
key = {string1:string}
try:
	dec_file = open('corrupted.bin')
	res_file = open('restored.bin', 'w')
	string_res = dec_file.read()
	string_write = key[string_res]
	res_file.write(string_write)
	dec_file.close()
	res_file.close()
except KeyError:
	res_file = open('restored.bin', 'w')
	res_file.write('CANNOT BE RESTORED')
	res_file.close()	








