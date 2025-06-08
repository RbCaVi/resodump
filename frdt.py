# resonite frdt data tree format reader
# taken from Elements.Assets.dll with dotpeek

# 9 byte header:
#   magic - 4 bytes - 70 114 68 84 - 'FrDT'
#   version - 4 bytes - currently 0
#   compression - 1 byte - 1 = lz4, 2 = lzma, 3 = brotli - technically 7bit encoded
# then the rest of the file is compressed bson

import struct
import brotli
import bson

def read(frdtdata):
  # read an frdt file into a json object
  (magic, version, compression) = struct.unpack('<4sib', frdtdata[:9])
  assert magic == b'FrDT'
  assert version == 0
  assert compression in [1, 2, 3]
  compressed = frdtdata[9:]
  if compression == 1:
    # lz4
    assert False, 'lz4 compression not supported'
  if compression == 2:
    # lzma
    assert False, 'lzma compression not supported'
  if compression == 3:
    # brotli
    frdtbson = brotli.decompress(compressed)
  return bson.loads(frdtbson)

def write(tree):
  return struct.pack('<4sib', b'FrDT', 0, 3) + brotli.compress(bson.dumps(tree))