import frdtgen

import json

with open('test-tool.json', 'r') as f:
  tree = json.load(f)

out,assethashes = frdtgen.generate(tree)

import frdt

import resonitepackage
import datetime

now = datetime.datetime.now(datetime.timezone.utc).isoformat()[:-6] + 'Z' # snip off the +00:00 at the end to match the format from resonite
me = 'U-1YuDa214TQG'

mainrecord = {
  'creationTime': now,
  'description': None,
  'firstPublishTime': None,
  'id': 'R-Main',
  'isDeleted': False,
  'isForPatrons': False,
  'isListed': False,
  'isPublic': False,
  'isReadOnly': False,
  'lastModificationTime': now,
  'migrationMetadata': None,
  'name': out['Object']['Name']['Data'],
  'ownerId': me,
  'ownerName': None,
  'path': None,
  'randomOrder': 0,
  'rating': 0,
  'recordType': 'object',
  'submissions': None,
  'tags': None,
  'thumbnailUri': None,
  'version': {
    'globalVersion': 0,
    'lastModifyingMachineId': None,
    'lastModifyingUserId': None,
    'localVersion': 0
  },
  'visits': 0
}

assetmanifest = []

import meshx

with open('out/tool.meshx', 'wb') as f:
  mesh = {
    'vertices': [
      (-0.125, -0.125, -0.125),
      ( 0.125, -0.125, -0.125),
      (-0.125,  0.125, -0.125),
      ( 0.125,  0.125, -0.125),
      (-0.125, -0.125,  0.125),
      ( 0.125, -0.125,  0.125),
      (-0.125,  0.125,  0.125),
      ( 0.125,  0.125,  0.125),
    ],
    'meshes': [[
      (0, 1, 3),
      (0, 2, 3),
      (4, 5, 7),
      (4, 6, 7),
      (0, 1, 5),
      (0, 4, 5),
      (2, 3, 7),
      (2, 6, 7),
      (0, 2, 6),
      (0, 4, 6),
      (1, 3, 7),
      (1, 5, 7),
    ]],
  }
  f.write(meshx.write(mesh))

with resonitepackage.ResonitePackage('out/test-tool.resonitepackage', 'w') as package:
  for a,h in assethashes.items():
    with open(a, 'rb') as f:
      data = f.read()
      package.addasset(h, data)
      assetmanifest.append({'hash': h, 'bytes': len(data)})
  maindata = frdt.write(out)
  mainhash = hex(0x20000000000000000 +hash(maindata))[3:] * 4
  package.addasset(mainhash, maindata)
  mainrecord['assetManifest'] = assetmanifest
  mainrecord['assetUri'] = 'packdb:///' + mainhash
  package.setmainrecord(mainrecord)