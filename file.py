words = 0
with open('referat.txt', 'r', encoding='utf-8') as f:
    for line in f:
    	words=words+len(line.split(' '))
print(words)    	
        
