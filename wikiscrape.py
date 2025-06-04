url = 'https://wiki.resonite.com/api.php?action=query&list=categorymembers&format=json&cmtitle=Category:Components&cmprop=title|type'

import requests
import pprint
import mediawiki
import xml.etree.ElementTree

wiki = mediawiki.MediaWiki(url = 'https://wiki.resonite.com/api.php', user_agent = "rbcavi on discord or github :)'); DROP TABLE users; --")

components = wiki.categorymembers('Components', results = None, subcategories = False)

pprint.pprint(components)

wiki.page(components[0])

headers = {'User-Agent' : "rbcavi on discord or github :)'); DROP TABLE users; --"}

def splitby(pred, l):
  return [x for x in l if pred(x)], [x for x in l if not pred(x)]

xd = xml.etree.ElementTree.dump

for component in components[0:]:
  url = f'https://wiki.resonite.com/api.php?action=parse&format=json&prop=sections&page={component}'
  componenttable = requests.get(url).json()
  pprint.pprint(componenttable)
  
  url = f'https://wiki.resonite.com/api.php?action=parse&format=json&prop=parsetree&section=1&page={component}'
  componenttable = requests.get(url).json()
  pprint.pprint(componenttable)
  xmltable = xml.etree.ElementTree.fromstring(componenttable['parse']['parsetree']['*'])
  pprint.pprint(xmltable)
  assert xmltable[1][0].text.strip() == 'Table ComponentFields'
  assert len(xmltable[1]) == len(xmltable[1].findall('part')) + 1
  print(xml.etree.ElementTree.dump(xmltable[1]))
  fieldxmls,advxmls = splitby(lambda e: 'index' in e[0].attrib, xmltable[1].findall('part'))
  assert len(fieldxmls) % 3 == 0
  for name,eq,val in advxmls:
    assert name.tag == 'name'
    assert name.text.startswith('TypeAdv')
    assert eq.tag == 'equals'
    assert eq.text == '='
    assert val.tag == 'value'
    assert val.text == 'true'
  advidxs = [int(name.text[len('TypeAdv'):]) - 1 for name,eq,val in advxmls]
  for i,(name,val) in enumerate(fieldxmls):
    assert name.tag == 'name'
    assert int(name.attrib['index']) == i + 1
    assert val.tag == 'value'
  fields = [val.text for name,val in fieldxmls]
  fields = [*zip(fields[0::3], fields[1::3], fields[2::3])]
  break