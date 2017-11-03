import os

keywords = {}

for root, dirs, files in os.walk('./Clojure/'):
	for filename in files:
		if filename.endswith('.cl'):			
			with open('./Clojure/' + filename) as file:
				raw_code = file.read().splitlines()
				for line in raw_code:
					words = line.split(' ')
					for word in words:
						if word.strip().startswith('('):
							word = word.replace('(', '').replace(')', '')
							if not word in keywords:
								keywords[word] = 1
							else:
								keywords[word] += 1



for word in sorted(keywords, key=keywords.get, reverse=False):
	if len(word) > 1 and word[0].isalpha():
		print (word + ': ' + str(keywords[word]))



