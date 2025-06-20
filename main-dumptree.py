# dump a .resonitepackage's main object to out/tree.json

import json
import sys

import resonitepackage

packagename = sys.argv[1]

package = resonitepackage.ResonitePackage(packagename)
tree = package.getmainasset()

import pprint

#pprint.pprint(package.getmainrecord())

with open('out/tree.json', 'w') as f:
  json.dump(tree, f)