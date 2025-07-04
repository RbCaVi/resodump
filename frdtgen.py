# convert a partially implicit/simplified json representation of a resonite object into an frdt

import itertools

import pfmain

import pprint

def generateids():
  for i in itertools.count():
    assert i < 0x100000000 # a reasonable limit, right? 4 billion? surely
    # like i guess i could write uuids properly
    # but nobody's going to use even a million slots right?
    yield hex(0x100000000 + i)[3:] + '-0000-0000-0000-000000000000'

class FrdtGenContext:
  def __init__(self):
    self.ids = generateids()
    self.idmap = {}
    self.types = []
    self.assethashes = {}
    self.fluxids = itertools.count()
  
  def getid(self):
    return next(self.ids)

  def processobject1(self, o):
    # defaults and ids
    # an object has a defined set of properties
    # name is required
    # tag = null, active = true
    # children = [], components = []
    # position = [0, 0, 0], rotation = [0, 0, 0, 1], scale = [1, 1, 1]
    # orderoffset = 0
    # id, persistent-id, and parentreference are autogenerated
    assert 'Name' in o
    o.setdefault('Tag', None)
    o.setdefault('Active', True)
    o.setdefault('Children', [])
    o.setdefault('Components', [])
    o.setdefault('Position', [0, 0, 0])
    o.setdefault('Rotation', [0, 0, 0, 1])
    o.setdefault('Scale', [1, 1, 1])
    o['OrderOffset'] = 0
    o['ID'] = '###id###'
    o['Persistent-ID'] = '###id###'
    o['ParentReference'] = '###id###'
    idp = o.pop('id', None)
    out = {}
    out['Children'] = [self.processobject1(c) for c in o.pop('Children')]
    out['Components'] = [self.processcomponent1(c) for c in o.pop('Components')]
    for prop,value in o.items():
      if value == '###id###': # no sane person will put this as a string value right?
        value = self.getid()
      else:
        value = self.processvalue1(value)
        if type(value) != dict or 'ID' not in value:
          # wrap a normal value in a member with an id
          value = {"ID": self.getid(), "Data": value}
      out[prop] = value
    if idp is not None:
      self.idmap[idp] = out['ID']
    return out

  def processcomponent1(self, c):
    # defaults and ids
    # a component has some default properties
    # and others as well
    # type is required
    # enabled = true
    # updateorder = 0
    # id and persistent-id are autogenerated
    assert 'type' in c
    if c['type'] not in self.types:
      self.types.append(c['type'])
    c['type'] = self.types.index(c['type'])
    c.setdefault('Enabled', True)
    c.setdefault('UpdateOrder', 0)
    c['ID'] = '###id###'
    c['persistent-ID'] = '###id###'
    idp = c.pop('id', None)
    out = {}
    out['type'] = c.pop('type')
    for prop,value in c.items():
      if value == '###id###': # no sane person will put this as a string value right?
        value = self.getid()
      else:
        value = self.processvalue1(value)
        if type(value) != dict or 'ID' not in value:
          value = {"ID": self.getid(), "Data": value}
      out[prop] = value
    if idp is not None:
      self.idmap[idp] = out['ID']
    return out

  def processasset1(self, a):
    # defaults and ids
    # an asset has some default properties
    # and others as well
    # type is required
    # enabled = true
    # updateorder = 0
    # persistent = false
    # id is autogenerated
    assert 'type' in a
    if a['type'] not in self.types:
      self.types.append(a['type'])
    a['type'] = self.types.index(a['type'])
    a.setdefault('Enabled', True)
    a.setdefault('UpdateOrder', 0)
    a.setdefault('persistent', False)
    a['ID'] = '###id###'
    idp = a.pop('id', None)
    out = {}
    out['type'] = a.pop('type')
    for prop,value in a.items():
      if value == '###id###': # no sane person will put this as a string value right?
        value = self.getid()
      else:
        value = self.processvalue1(value)
        if type(value) != dict or 'ID' not in value:
          value = {"ID": self.getid(), "Data": value}
      out[prop] = value
    if idp is not None:
      self.idmap[idp] = out['ID']
    return out

  def processvalue1(self, v):
    # values are more flexible than objects and components
    # they don't always have an id key tbh
    if type(v) == dict:
      if 'id' in v and 'ID' not in v:
        v['ID'] = '###id###'
      idp = v.pop('id', None)
      out = {}
      for prop,value in v.items():
        if value == '###id###': # no sane person will put this as a string value right?
          value = self.getid()
        else:
          value = self.processvalue1(value)
        out[prop] = value
      if idp is not None:
        self.idmap[idp] = out['ID']
      return out
    elif type(v) == list:
      return [self.processvalue1(sv) for sv in v]
    else:
      return v

  def processobject2(self, o):
    # resolve id references and restructure
    # objects actually don't have any id references
    o['Children'] = [self.processobject2(c) for c in o['Children']]
    o['Components'] = {'ID': self.getid(), 'Data': [self.processcomponent2(c) for c in o['Components']]}
    return o

  def processcomponent2(self, c):
    # resolve id references and restructure
    t = c.pop('type')
    for prop,value in c.items():
      c[prop] = self.processvalue2(value)
    return {'Type': t, 'Data': c}
    
  processasset2 = processcomponent2

  def processvalue2(self, v):
    # resolve id references
    if type(v) == dict:
      return {k: self.processvalue2(sv) for k,sv in v.items()}
    if type(v) == list:
      return [self.processvalue2(sv) for sv in v]
    if type(v) == str:
      if v.startswith('###') and v.endswith('###'):
        return self.idmap[v[3:-3]]
      if v.startswith('##@') and v.endswith('###'):
        self.assethashes[v[3:-3]] = hex(0x20000000000000000 +hash(v[3:-3]))[3:] * 4
        return '@packdb:///' + self.assethashes[v[3:-3]]
    return v

  def addprotoflux(self, o):
    # adds protoflux children to any slot with a 'source' key
    if 'source' in o:
      with open(o['source']) as f:
        s = f.read()
      o['Children'] = pfmain.generate(s, next(self.fluxids))
      #pprint.pprint(o['Children'])
      del o['source']
    else:
      if 'Children' in o:
        for c in o['Children']:
          self.addprotoflux(c)

def generate(tree):
  frdtcontext = FrdtGenContext()

  frdtcontext.addprotoflux(tree['Object'])

  o = frdtcontext.processobject1(tree['Object'])
  assets = [frdtcontext.processasset1(a) for a in tree['Assets']]

  o = frdtcontext.processobject2(o)
  assets = [frdtcontext.processasset2(a) for a in assets]

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
  
  return out, frdtcontext.assethashes