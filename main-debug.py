# main for debug stuff
# you should run this one with -i

import json
import pprint
import re

import resonitepackage
import frdt

packagename = 'Redprint Manager 2.4.zip'
packagename = 'out/inventory-tool.resonitepackage'

package = resonitepackage.ResonitePackage(packagename)
mainrecord = package.getmainrecord()

assetmanifest = mainrecord['assetManifest']
del mainrecord['assetManifest']

#pprint.pprint(mainrecord)

mainfrdt = package.getasset(mainrecord['assetUri'])
tree = frdt.read(mainfrdt)

# get a list of all ids of things and where they are
# and almost everything has an id
# objects, components, and data fields
# data fields presumably for things like driven fields
idpaths = {}
def walkforids(tree, path = ()):
  if type(tree) == dict:
    if 'ID' in tree:
      assert tree['ID'] not in idpaths
      idpaths[tree['ID']] = path
    for k,v in tree.items():
      walkforids(v, path + (k,))
  if type(tree) == list:
    for i,v in enumerate(tree):
      walkforids(v, path + (i,))

walkforids(tree)

# anytime an id is referenced in a `Data` key (usually of a field i think)
# add a 'path' key to show where that id may be found
def lookupids(tree):
  if type(tree) == dict:
    if 'Data' in tree and type(tree['Data']) == str and tree['Data'] in idpaths:
      tree['path'] = idpaths[tree['Data']]
    for k,v in tree.items():
      lookupids(v)
  if type(tree) == list:
    for i,v in enumerate(tree):
      lookupids(v)

lookupids(tree)

# anytime a type is referenced in a `Type` key
# add a 'type' key to show its name (found in `toplevel.Types`)
def lookuptypes(tree, types):
  if type(tree) == dict:
    if 'Type' in tree and type(tree['Type']) == int:
        tree['type'] = types[tree['Type']]
    for v in tree.values():
      lookuptypes(v, types)
  if type(tree) == list:
    for v in tree:
      lookuptypes(v, types)

lookuptypes(tree, tree['Types'])

#o = {**tree['Object']['Children'][13]['Children'][2]['Children'][3]['Children'][6]}

#del o['Children']
#pprint.pprint(o)
#printobjecttree(o)

#tree2 = {**tree}

#del tree2['Object']
#del tree2['Assets']
#del tree2['Types']
#print(tree2.keys())
#pprint.pprint(tree2)

shorttypes = [re.sub('(^|<)[^<>,]*\\.', '', re.sub('<[^<>,]*\\.', '<', a)) for a in tree['Types']]

def printobjecttree(object, i = 0, indent = ''):
  components = object['Components']['Data']
  names = [('P*' if 'ProtoFlux' in tree['Types'][c['Type']] else '') + shorttypes[c['Type']] for c in components]
  names = [shorttypes[c['Type']] for c in components if 'ProtoFlux' not in tree['Types'][c['Type']]]
  print((indent + str(i).ljust(4) + re.sub('<[^>]+>', '', object['Name']['Data'])).ljust(80), ', '.join(names).ljust(80), object['ID'])
  for i,child in enumerate(object['Children']):
    printobjecttree(child, i, indent + str(i).ljust(4))

#printobjecttree(tree['Object'])

#pprint.pprint(tree['Assets'])

def findintree(tree, pattern, path = ()):
  if pattern not in str(tree):
    return
  if type(tree) == dict:
    down = [(k, v) for k,v in tree.items() if pattern in str(v)]
    for k,v in down:
      yield from findintree(v, pattern, path + (k,))
    if len(down) == 0:
      yield path
  elif type(tree) == list:
    down = [(i, v) for i,v in enumerate(tree) if pattern in str(v)]
    for i,v in down:
      yield from findintree(v, pattern, path + (i,))
    if len(down) == 0:
      yield path
  else:
    yield path