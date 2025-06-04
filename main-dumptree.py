# dump a .resonitepackage's main object to tree.json

import json

import resonitepackage
import readfrdt

packagename = 'Redprint Manager 2.4.zip'

package = resonitepackage.ResonitePackage(packagename)
tree = package.getmainasset()

with open('tree.json', 'w') as f:
  json.dump(tree, f)