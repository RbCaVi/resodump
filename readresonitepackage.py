def readb(f):
 with open(f, 'rb') as f:
  return f.read()

import os

def read(f):
 with open(f, 'r') as f:
  return f.read()

import json
def jread(f):
 with open(f) as f:
  return json.load(f)

import pprint
mainrecord = jread('R-Main.record')

'''
paths = [os.path.join(d, f) for d,_,fs in os.walk('.') for f in fs]
metas = os.listdir('Metadata')
assets = os.listdir('Assets')

len(mainrecord['assetManifest'])

pairedassets = [(a, [m for m in metas if a in m][0] if a in str(metas) else None) for a in assets]

for a,m in pairedassets:
  input()
  print(a, m)
  if m is not None:
    pprint.pprint(jread(os.path.join('Metadata', m)))
  print(readb(os.path.join('Assets', a))[:30])

pairedbitmaps = [(a, m) for a,m in pairedassets if m is not None and 'bitmap' in m]
pairedmeshes = [(a, m) for a,m in pairedassets if m is not None and 'mesh' in m]
pairedother = [(a, m) for a,m in pairedassets if m is None]

os.mkdir('out')
os.mkdir('out/bitmaps')
os.mkdir('out/meshes')
os.mkdir('out/other')

def copy(f1, f2):
  with open(f1, 'rb') as f1:
    with open(f2, 'wb') as f2:
      f2.write(f1.read())

for a,m in pairedbitmaps:
  ext = jread(os.path.join('Metadata', m))['baseFormat']
  copy(os.path.join('Metadata', m), os.path.join('out/bitmaps', m))
  copy(os.path.join('Assets', a), os.path.join('out/bitmaps', a + '.' + ext))

for a,m in pairedmeshes:
  copy(os.path.join('Metadata', m), os.path.join('out/meshes', m))
  copy(os.path.join('Assets', a), os.path.join('out/meshes', a))

for a,m in pairedother:
  copy(os.path.join('Assets', a), os.path.join('out/other', a))

for f in os.listdir('out/meshes'):
 input()
 if 'mesh' in f:
  pprint.pprint(jread(os.path.join('out/meshes', f)))
 else:
  print(readb(os.path.join('out/meshes', f))[:100])

for f in os.listdir('out/other'):
 input()
 print(f, readb(os.path.join('out/other', f))[:100])

for f in os.listdir('out/meshes'):
 input()
 if 'mesh' in f:
  pprint.pprint(jread(os.path.join('out/meshes', f)))

for f in os.listdir('out/bitmaps'):
 input()
 if 'bitmap' in f:
  pprint.pprint(jread(os.path.join('out/bitmaps', f)))
'''

for a in mainrecord['assetManifest']:
  assert len(readb(os.path.join('Assets', a['hash']))) == a['bytes']

del mainrecord['assetManifest']

pprint.pprint(mainrecord)

ownerid = mainrecord['ownerId']

import requests

headers = {'User-Agent' : "rbcavi on discord :)'); DROP TABLE users; --"}

ownerinfo = requests.get(f'https://api.resonite.com/users/{ownerid}').json()

print(f"This object was owned by {ownerinfo['username']}")

def readpackdb(uri):
  assert uri.startswith('packdb:///')
  assethash = uri[len('packdb:///'):]
  return readb(os.path.join('Assets', assethash))

# FrDT format

# i got this from dotpeek ;)

# header:
# b'FrDT'
# version i32
# compression 7bitencoded = None LZ4 LZMA Brotli
# 7bitencoded is 7 bits + top bit to continue
# there are only four values though, so this can just be a single byte field

import struct
import brotli
import bson

def unpackstart(fmt, data):
  size = struct.calcsize(fmt)
  return struct.unpack(fmt, data[:size]), data[size:]

def unpackheader(data):
  header,data = unpackstart('<4sib', data)
  assert header[0] == b'FrDT', "Missing magic number"
  assert not (header[1] > 0), "Version too new"
  assert header[2] in [1, 2, 3], "Invalid compression"
  return (header[1], header[2]), data

def readfrdt(filedata):
  C_LZ4 = 1
  C_LZMA = 2
  C_BROTLI = 3

  header,compressed = unpackheader(filedata)

  databson = brotli.decompress(compressed)

  data = bson.loads(databson)
  
  return data

with open('debug.txt', 'w') as f:
  pass # delete the file contents

def d(s):
  with open('debug.txt', 'a') as f:
    f.write(s + '\n')

paths = {}
def getpaths(data, path = ()):
  if type(data) == dict:
    if 'ID' in data:
      assert data['ID'] not in paths
      paths[data['ID']] = path
    for k,v in data.items():
      getpaths(v, path + (k,))
  elif type(data) == list:
    for i,v in enumerate(data):
      getpaths(v, path + (i,))

def ss(x):
  if type(x) == dict:
    return {k:(type(v).__name__, len(str(v))) for k,v in x.items()}
  else:
    return [(type(v).__name__, len(str(v))) for v in x]

tree = readfrdt(readpackdb(mainrecord['assetUri']))
getpaths(tree)