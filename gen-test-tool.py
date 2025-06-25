import frdtgen

import json

with open('test-tool.json', 'r') as f:
  tree = json.load(f)

frdtcontext = frdtgen.FrdtGenContext()

frdtcontext.addprotoflux(tree['Object'])

o = frdtcontext.processobject1(tree['Object'])
assets = [frdtcontext.processasset1(a) for a in tree['Assets']]

#print(idmap)

o = frdtcontext.processobject2(o)
assets = [frdtcontext.processasset2(a) for a in assets]

import pprint

out = {
  "VersionNumber": "2025.5.23.1096",
  "FeatureFlags": {
    "ColorManagement": 0,
    "ResetGUID": 0,
    "ProtoFlux": 0,
    "TEXTURE_QUALITY": 0,
    "TypeManagement": 0,
    "ALIGNER_FILTERING": 0,
    "PhotonDust": 0,
    "Awwdio": 0
  },
  "TypeVersions": {
    # what do i put here
    # can i use some kind of.... reflection?
  }
}

out['Types'] = frdtcontext.types
out['Assets'] = assets
out['Object'] = o

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
  for a,h in frdtcontext.assethashes.items():
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