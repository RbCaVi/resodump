# dump a .resonitepackage's main object to tree.json

import json

import resonitepackage

packagename = 'Redprint Manager 2.4.zip'
packagename = 'out/inventory-tool.resonitepackage'

package = resonitepackage.ResonitePackage(packagename)
tree = package.getmainasset()

import pprint

#pprint.pprint(package.getmainrecord())

with open('tree.json', 'w') as f:
  json.dump(tree, f)