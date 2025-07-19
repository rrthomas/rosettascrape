#!/usr/bin/env python3

import os
import os.path
import sys
from pathlib import Path
from threading import Thread

import pygments.lexers
import requests
from lxml import etree, html


page_downloads = {}

headers = {
    "User-Agent": "rosettascrape/0.1 (https://github.com/rrthomas/rosettascrape; rrt@sc3d.org)"
}

class RosettaScraper(Thread):

	def __init__(self, language):
		Thread.__init__(self)    
		self.l = language
		self.e = Path(pygments.lexers.find_lexer_class_by_name(language).filenames[0]).suffix

	def run(self): 

		language = self.l
		extension = self.e

		if not os.path.exists(language):
			os.makedirs(language)
	
		html_source = ''

		if os.path.isfile('.html/#' + language.replace(' ', '_') + '.html'):
			with open('.html/#' + language.replace(' ', '_') + '.html', 'r') as content_file:    
				html_source = content_file.read()
		else:
			page = requests.get('https://rosettacode.org/wiki/Category:{0}'.format(language.replace(' ', '_')), headers=headers)
			html_source = str(page.text)

			with open('.html/#' + language.replace(' ', '_') + '.html', 'w') as content_file:    
				content_file.write(html_source)

		tree = html.fromstring(html_source)

		results = tree.xpath('//div[@id="mw-pages"]//a')

		for it in results:	
			description = it.text_content().replace('/', ' - ')
			filename = language + '/' + ''.join(c for c in description if c.isalnum() or c in (' ','.','_')).rstrip() 

			href = it.attrib['href']		

			if href in page_downloads:							
				while page_downloads[href] == False:
					pass

			if os.path.isfile('.html/' + href.replace('/wiki/', '').replace('/', ' - ') + '.html'):
				with open('.html/' + href.replace('/wiki/', '').replace('/', ' - ') + '.html', 'r') as content_file:    
					html_source = content_file.read()
			else:
				page_downloads[href] = False
				subpage = requests.get('https://rosettacode.org' + href, headers=headers)
				html_source = str(subpage.text)
				with open('.html/' + href.replace('/wiki/', '').replace('/', ' - ') + '.html', 'w') as content_file:    
					content_file.write(html_source)
				page_downloads[href] = True

			subtree = html.fromstring(html_source)

			#print (html_source)

			subresults = subtree.xpath('//*[@id="mw-content-text"]/div[contains(@class, "mw-parser-output")]/*')

			additional = ''
			note = ''
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
						
						with open(filename + note + '.txt', 'a') as f:
							f.write(node.text_content())

						if note == '':
							note = ' i'
						note += 'i'

				if not process_node:

					if node.tag == 'h2' and node.text_content().replace('[edit]', '').strip() == language:
						
						process_node = True
				else:
					if node.tag == 'h2' and not node.text_content().replace('[edit]', '') == language:
						break

			print ()	


scanners = []

if not os.path.exists('.html'):
	os.makedirs('.html')

languages = sys.argv[1:]

for language in languages:
	scanner = RosettaScraper(language)
	scanner.start()

for scanner in scanners:
	scanner.join()
