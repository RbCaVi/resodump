# find all mesh assets and decode them into json
# put the json into out/

import os
import json
import sys
import io

import resonitepackage
import meshx
import lz4

import timer

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
        data = lz4.lz4decompress(io.BytesIO(data))
        if not data.read(6) == b'\x05MeshX':
          print('nope')
          continue
      except:
        # there's only one place that can throw exceptions, right?
        # (i'm assuming all errors here come from lz4.lz4decompress())
        print('nope')
        continue
    print(f'yes, {len(data)} bytes')
    with open(os.path.join('out', assethash + '-mesh.json'), 'w') as f:
      with timer.timer('mesh'):
        m = meshx.read(data)
      json.dump(m, f)
