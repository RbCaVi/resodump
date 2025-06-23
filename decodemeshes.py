# find all mesh assets and decode them into json
# put the json into out/

import os
import json
import sys

import resonitepackage
import meshx

#packagename = 'Redprint Manager 2.4.zip'
#packagename = 'out/inventory-tool.resonitepackage'
packagename = sys.argv[1]

with resonitepackage.ResonitePackage(packagename) as package:
  for assethash in package.assetlist():
    print('trying', assethash)
    data = package.getasset(assethash)
    if not data.startswith(b'\x05MeshX'):
      # i don't know if this is worth it (checking if it's a compressed meshx file)
      try:
        data = lz4.lz4decompress(data)
      except:
        # there's only one place that can throw exceptions, right?
        # (i'm assuming all errors here come from lz4.lz4decompress())
        print('nope')
        continue
      if not data.startswith(b'\x05MeshX'):
        print('nope')
        continue
    print(f'yes, {len(data)} bytes')
    with open(os.path.join('out', assethash + '-mesh.json'), 'w') as f:
      json.dump(meshx.read(data), f)
