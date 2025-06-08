# .resonitepackage class
# a .resonitepackage is a renamed zip file
# it has three items (as far as i know)
#   main record (R-main.record) - a json file
#   assets (Assets/) - assets named by their hashes
#   metadata (Metadata/) - metadata for some assets - named <hash of associated asset>.<type (mesh or bitmap, as far as i know)>

import zipfile
import json
import os

import frdt

class ResonitePackage:
  # wrapper around ZipFile to get assets and main record from a .resonitepackage file
  # there is also metadata, but i didn't 
  def __init__(self, file):
    # `file` can be a path or a file object
    self.zipfile = zipfile.ZipFile(file, 'r')
  
  def __enter__(self):
    return self
  
  def getmainrecord(self):
    with self.zipfile.open('R-Main.record') as recordf:
      return json.load(recordf)
  
  def getmainasset(self):
    mainrecord = self.getmainrecord()
    frdtdata = self.getasset(mainrecord['assetUri'])
    tree = frdt.read(frdtdata)
    return tree

  def getasset(self, asset):
    if asset.startswith('packdb:///'):
      assethash = asset[len('packdb:///'):]
    else:
      assethash = asset
    with self.zipfile.open(f'Assets/{assethash}') as assetf:
      return assetf.read()

  def assetlist(self):
    return [os.path.basename(p) for p in self.zipfile.namelist() if 'Assets' in p]
  
  def __exit__(self, type, value, tb):
    self.zipfile.close()
  
  def close(self):
    self.zipfile.close()