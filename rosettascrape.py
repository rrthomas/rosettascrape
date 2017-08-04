from lxml import html
from lxml import etree
import requests

language = input ('Which language?')
extension = input ('Which file extension?')

if (extension[0] != '.'):
	extension = '.' + extension

page = requests.get('http://rosettacode.org/wiki/Category:{0}'.format(language.replace(' ', '_')))
tree = html.fromstring(page.content)

results = tree.xpath('//div[@id="mw-pages"]//a')

for it in results:	
	filename = ''.join(c for c in it.text_content() if c.isalnum() or c in (' ','.','_')).rstrip() + extension
	title = '{0} -> {1}'.format(it.text_content(), filename)
	href = it.attrib['href']
	print('\n{0}\n{1}\n{0}'.format('-' * len(title), title))

	subpage = requests.get('http://rosettacode.org' + href)
	subtree = html.fromstring(subpage.content)

	subresults = subtree.xpath('//*[@id="mw-content-text"]/*')

	next_node = False
	for node in subresults:
		if next_node and node.tag == 'pre':
			
			code = etree.tostring(node, encoding='unicode', with_tail=False)			

			with open(filename, 'w') as f:

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

			break

		if node.tag == 'h2' and node.text_content() == language:
			next_node = True

	print ()	
