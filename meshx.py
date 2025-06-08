# resonite meshx mesh format reader
# internal mesh format used by resonite (and neosvr before it)
# taken from Elements.Assets.dll with dotpeek

# a string is encoded as 7bit encoded length and <length> bytes of string

# so many versions....

# technically the whole file can be compressed with lz4, but this doesn't handle that

# the header (fields are only parsed if the version matches):
#   magic - 6 bytes - 5 77 101 115 104 88 - '\x05MeshX'
#   version - 4 bytes - 0 to 7 (maybe 1 to 7)
#   flags - 4 bytes - read from least significant to most significant
#     1 - has normals
#     2 - has tangents
#     4 - has colors
#     8 - has bone bindings (and presumably bones)
#   number of vertices - 7bit encoded
#   number of triangles (version 0, 1, 2) or meshes (version 3, 4, 5, 6, 7) - 7bit encoded
#   number of bones - 7bit encoded
#   number of blendshapes (version 4, 5, 6, 7) - 7bit encoded
#   number of models (version 1, 2) - 7bit encoded
#   uvs (version 6, 7):
#     number of uvs - 7bit encoded
#     uv dimensionality - <number of uvs> bytes - all 2, 3, or 4
#     put into the uv array sequentially
#   otherwise (version 1, 2, 3, 4, 5):
#     uvs are all 2d and only present with corresponding flags
#     there are 4 uvs
#     the flags in question: bits 5-8 (16, 32, 64, 128)
#   color profile (version 7) - string - Linear, sRGB, or sRGBAlpha
#   compression (version 2, 3, 4, 5, 6, 7) - 1 byte - 0 = none, 1 = lz4, 2 = lzma - determines the compression method of the rest of the file - technically 7bit encoded

# the rest of the file data (possibly compressed):

# vertices - <number of vertices> * 3 floats
# normals, tangents, colors, bone bindings may be omitted, corresponding to the flags
# normals - <number of vertices> * 3 floats
# tangents - <number of vertices> * 4 floats - i'm not sure how to interpret these
# colors - <number of vertices> * 4 floats
# bone bindings - <number of vertices> * 4 7bit encoded ints and 4 floats - the ints are the indexes of bones and the floats are the weights - weights are normalized in version 0, 1, 2, 3, 4
# uvs - <number of vertices> * <uv dimension> floats for each uv

# meshes (version 3, 4, 5, 6, 7):
#   for each mesh:
#     type - string - Points (1 index) or Triangles (3 indices)
#     primitive count - 7bit encoded
#     primitive indices into vertex and other arrays - <primitive count> * <number of indices> ints
# mesh (number of models = 1 or version 0):
#   triangle indices - <number of triangles> * 3 ints
# meshes (version 1, 2):
#   triangle indices - <number of triangles> * 3 ints
#   mesh indices - <number of triangles> * 1 int - all less than number of models
#   triangles are sorted into meshes by the corresponding mesh index

# bones:
#   for each bone:
#     name - string
#     bind pose - 4x4 float matrix

# blendshapes:
#   for each blendshape:
#     name - string - unique
#     flags - 7bit encoded
#       1 - has normals
#       2 - has tangents
#     number of frames - 7bit encoded
#     for each frame:
#       weight - float
#       vertices, normals, tangents - same as top level

import unpack
import lz4

def unpackheader(data):
  (magic,version,flags),data = unpack.unpackstruct('<6sii', data)
  vertexcount,data = unpack.unpack7bit(data)
  meshsize,data = unpack.unpack7bit(data)
  bonecount,data = unpack.unpack7bit(data)
  assert magic == b'\x05MeshX', 'no header, try decompressing with LZ4 :)'
  assert version <= 7, 'version too high :('
  out = {
    'version': version,
    'flags': flags,
    'hasnormals': bool(flags & 1),
    'hastangents': bool(flags & 2),
    'hascolors': bool(flags & 4),
    'hasbonebindings': bool(flags & 8),
    'vertexcount': vertexcount,
    'bonecount': bonecount,
  }
  if version >= 3:
    out['meshcount'] = meshsize
  else:
    out['tricount'] = meshsize
  if version >= 4:
    blendshapecount,data = unpack.unpack7bit(data)
    out['blendshapecount'] = blendshapecount
  if version >= 1 and version < 3:
    modelcount,data = unpack.unpack7bit(data)
    out['modelcount'] = modelcount
  if version >= 6:
    uvcount,data = unpack.unpack7bit(data)
    uvdims,data = unpack.unpackbytes(uvcount, data)
    out['uvdims'] = [*enumerate(uvdims)]
  else:
    out['uvdims'] = [(i, 2) for i,f in enumerate([flags & 16, flags & 32, flags & 64, flags & 128]) if f]
  if version > 6:
    # read a string or something to an enum
    # Linear, sRGB, sRGBAlpha
    colorprofile,data = unpackstring(data)
    assert colorprofile in [b'Linear', b'sRGB', b'sRGBAlpha']
    out['colorprofile'] = colorprofile
  else:
    out['colorprofile'] = 'sRGB'
  
  if version >= 2:
    # technically 7bit encoded, but there are only three values
    # Plain (0), LZ4 (1), LZMA (2)
    (compression,),data = unpack.unpackstruct('<b', data)
    out['compression'] = compression
    if compression == 0:
      # no compression
      pass
    if compression == 1:
      data = lz4.lz4decompress(data)
    if compression == 2:
      # i don't have to do this rn
      assert False, 'lzma compression not supported yet - RbCaVi ;)'
  
  return out, data

def unpackfloat2(data):
  return unpack.unpackstruct('<ff', data)

def unpackfloat3(data):
  return unpack.unpackstruct('<fff', data)

def unpackfloat4(data):
  return unpack.unpackstruct('<ffff', data)

def unpackcolor(data):
  return unpack.unpackstruct('<ffff', data)

def unpackint3(data):
  return unpack.unpackstruct('<iii', data)

def unpackint(data):
  (i,),data = unpack.unpackstruct('<i', data)
  return i, data

def unpackbonebinding(data):
  i1,data = unpack.unpack7bit(data)
  i2,data = unpack.unpack7bit(data)
  i3,data = unpack.unpack7bit(data)
  i4,data = unpack.unpack7bit(data)
  weights,data = unpack.unpackstruct('<ffff', data)
  return ((i1, i2, i3, i4), weights), data

def unpackstring(data):
  length,data = unpack.unpack7bit(data)
  return unpack.unpackbytes(length, data)

def unpackn(unpackx, count, data):
  xs = []
  for i in range(count):
    x,data = unpackx(data)
    xs.append(x)
  return xs, data

def normalizebonebinding(b):
  idxs,weights = b
  totalweight = sum(weights)
  weights = tuple(w / totalweight for w in weights)
  return idxs, weights

def read(data):
  header,data = unpackheader(data)
  version = header['version']
  vertcount = header['vertexcount']

  #print(header)
  #print(vertcount, 'vertices')

  out = {}

  vertices,data = unpackn(unpackfloat3, vertcount, data)
  out['vertices'] = vertices

  if header['hasnormals']:
    normals,data = unpackn(unpackfloat3, vertcount, data)
    out['normals'] = normals

  if header['hastangents']:
    tangents,data = unpackn(unpackfloat4, vertcount, data)
    out['tangents'] = tangents

  if header['hascolors']:
    colors,data = unpackn(unpackcolor, vertcount, data)
    out['colors'] = colors

  if header['hasbonebindings']:
    bonebindings,data = unpackn(unpackbonebinding, vertcount, data)
    if version < 5:
      bonebindings = [normalizebonebinding(b) for b in bonebindings]
    out['bonebindings'] = bonebindings

  uvs = []
  for i,dim in header['uvdims']:
    if dim == 2:
      uv,data = unpackn(unpackfloat2, vertcount, data)
      uvs.append((i, uv))
    elif dim == 3:
      uv,data = unpackn(unpackfloat3, vertcount, data)
      uvs.append((i, uv))
    elif dim == 4:
      uv,data = unpackn(unpackfloat4, vertcount, data)
      uvs.append((i, uv))
    else:
      print('weird uv dimension:', i, dim)
  out['uvs'] = uvs

  meshes = []
  if version >= 3:
    for i in range(header['meshcount']):
      meshtype,data = unpackstring(data)
      if meshtype == b'':
        continue
      assert meshtype in [b'Points', b'Triangles']
      primcount,data = unpack.unpack7bit(data)
      if meshtype == b'Triangles':
        tris,data = unpackn(unpackint3, primcount, data)
        meshes.append(tris)
      elif meshtype == b'Points':
        points,data = unpackn(unpackint, primcount, data)
        meshes.append(points)
  elif header['modelcount'] == 1: # version == 0?
    tris,data = unpackn(unpackint3, header['tricount'], data)
    meshes.append(tris)
  else:
    tris,data = unpackn(unpackint3, header['tricount'], data)
    trimeshes,data = unpackn(unpackint, header['tricount'], data)
    meshes = [[] for _ in range(header['modelcount'])]
    for tri,meshidx in zip(tris, trimeshes):
      meshes[meshidx].append(tri)
  out['meshes'] = meshes

  bones = []
  for i in range(header['bonecount']):
    name,data = unpackstring(data)
    bindpose,data = unpackn(unpackfloat4, 4, data)
    bones.append({
      'name': name,
      'bindpose': tuple(bindpose),
    })

  blendshapes = {}
  for i in range(header['blendshapecount']):
    name,data = unpackstring(data)
    assert name not in blendshapes, 'duplicate blendshape :('
    blendshape = []
    flags,data = unpack.unpack7bit(data)
    hasnormals = bool(flags & 1)
    hastangents = bool(flags & 2)
    framecount,data = unpack.unpack7bit(data)
    for i in range(framecount):
      frame = {}
      # is this weight? maybe some kind of time? idk i just read the code
      # i know normalizeframeweights() sets them to an equally spaced range
      (weight,),data = unpack.unpackstruct('<f', data)
      frame['weight'] = weight
      vertices,data = unpackn(unpackfloat3, vertcount, data)
      frame['vertices'] = vertices
      if hasnormals:
        normals,data = unpackn(unpackfloat3, vertcount, data)
        frame['normals'] = normals
      if hastangents:
        tangents,data = unpackn(unpackfloat3, vertcount, data)
        frame['tangents'] = tangents
      blendshape.append(frame)
    blendshapes[name.decode('utf-8')] = blendshape
  out['blendshapes'] = blendshapes

  assert len(data) == 0, 'file had extra data at the end'

  return out