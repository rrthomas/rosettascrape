from threading import Thread
from lxml import html
from lxml import etree
import requests
import os
import os.path

languages = {'Kotlin': '.kt', 
			 'C#': '.cs',
			 'Ruby': '.rb', 
			 'JavaScript': '.js', 
			 'Lua': '.lua', 
			 'Python': '.py', 
			 'Java': '.java', 
			 'C++': '.cpp', 			 
			 'Go': '.go', 			 
			 'Perl 6': '.p6',
			 'PHP': '.php',
			 'Groovy': '.groovy',
			 'CoffeeScript': '.coffee',
			 'Haskell': 'hs'}

class RosettaScraper(Thread):

	def __init__(self, language, extension):
		Thread.__init__(self)    
		self.l = language
		self.e = extension

	def run(self): 

		language = self.l
		extension = self.e

		if not os.path.exists(language):
			os.makedirs(language)
	
		page = requests.get('http://rosettacode.org/wiki/Category:{0}'.format(language.replace(' ', '_')))
		tree = html.fromstring(page.content)

		results = tree.xpath('//div[@id="mw-pages"]//a')

		for it in results:	
			description = it.text_content().replace('/', ' - ')
			filename = language + '/' + ''.join(c for c in description if c.isalnum() or c in (' ','.','_')).rstrip() 

			if os.path.isfile(filename + extension):
				continue

			href = it.attrib['href']
			
			subpage = requests.get('http://rosettacode.org' + href)
			subtree = html.fromstring(subpage.content)

			subresults = subtree.xpath('//*[@id="mw-content-text"]/*')

			additional = ''
			process_node = False
			for node in subresults:

				if process_node:
					
					if node.tag == 'pre' or node.tag == 'code':
					
						code = etree.tostring(node, encoding='unicode', with_tail=False)			

						title = '{0} : {1} -> {2}'.format(language, it.text_content(), filename + additional + extension)
						print('\n{0}\n{1}\n{0}'.format('-' * len(title), title))

						with open(filename + additional + extension, 'w') as f:					

							tag = ''
							snippet = ''
							in_tag = False
							for char in code:
								if char == '<':
									in_tag = True
									if tag.lower().startswith('br'):
										print()
										f.write('\n')
									tag = ''
								elif char == '>':
									in_tag = False				
									snippet = snippet.replace(chr(160), '')
									snippet = snippet.replace('&gt;', '>')
									snippet = snippet.replace('&lt;', '<')
									snippet = snippet.replace('&amp;', '&')
									print (snippet, end='')
									f.write(snippet)					
									snippet = ''
								else:
									if in_tag:
										tag += char
									else:
										snippet += char		

						if additional == '':
							additional = ' i'
						additional += 'i'

					elif not node.tag == 'h2':

						with open(filename + additional + '.txt', 'a') as f:

							f.write(node.text_content())

				if not process_node:
					if node.tag == 'h2' and node.text_content() == language:
						process_node = True
				else:
					if node.tag == 'h2' and not node.text_content() == language:
						break

			print ()	


scanners = []

for language, extension in languages.items():
	scanner = RosettaScraper(language, extension)
	scanner.start()

for scanner in scanners:
	scanner.join()
