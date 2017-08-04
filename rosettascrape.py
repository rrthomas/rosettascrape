from lxml import html
from lxml import etree
import requests

language = 'Lua'

#page = requests.get('http://rosettacode.org/wiki/99_Bottles_of_Beer')
page = requests.get('http://rosettacode.org/wiki/Category:{0}'.format(language))
tree = html.fromstring(page.content)

results = tree.xpath('//div[@id="mw-pages"]//a')

for it in results:	
	filename = ''.join(c for c in it.text_content() if c.isalnum() or c in (' ','.','_')).rstrip() + '.lua'
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
						print (snippet, end='')
						f.write(snippet)					
						snippet = ''
					else:
						if in_tag:
							tag += char
						else:
							snippet += char


			# new_line = True
			# for subnode in node:
			# 	if subnode.tag == 'br':
			# 		print ()
			# 		new_line = True
			# 	else:
			# 		subnodeclass = subnode.attrib['class']
			# 		if new_line:						
			# 			indent = subnodeclass[2]
			# 			print ('    ' * int(indent), end='')
			# 			new_line = False
			# 		if subnodeclass.startswith('kw'):
			# 			print (subnode.text_content(), end=' ')
			# 		else:
			# 			print (subnode.text_content(), end='')							

			break
		if node.tag == 'h2' and node.text_content() == language:
			next_node = True


		#subresults = subtree.xpath('//span[@id="{0}"]'.format(language)) #/ancestor/following-sibling
		#print (subresults)

	print ()	
	#break
