# try to find resonite asset types by magic numbers
# i know of five types of assets:
#   image - png or webp format - .bitmap metadata
#   sound - ogg or wav
#   font - ttf
#   mesh - resonite meshx format
#   object - resonite frdt format - only one in a .resonitepackage as far as i know

def assettype(data):
  # these first five are from https://en.wikipedia.org/wiki/List_of_file_signatures
  if data[:8] == b'\x89PNG\r\n\x1a\n':
    return ('bitmap', 'png')
  if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
    return ('bitmap', 'webp')
  if data[:4] == b'RIFF' and data[8:12] == b'WAVE':
    return ('sound', 'wav')
  if data[:4] == b'OggS':
    return ('sound', 'ogg')
  if data[:5] == b'\x00\x01\x00\x00\x00':
    return ('font', 'ttf')
  # these are custom formats from resonite (neosvr?)
  if data[:4] == b'FrDT':
    return ('object', 'frdt')
  if data[:6] == b'MeshX\x05':
    return ('mesh', 'meshx')
  try:
    decheader = lz4.lz4decompressstart(data, 6)
    if decheader[:6] == b'MeshX\x05':
      return ('mesh', 'meshx')
  except:
    # presumably an error in lz4.lz4decompressstart()
    pass
  return ('unknown', 'unknown')