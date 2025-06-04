# utility stream processing functions
# i think like c sharp binaryreader
# i call these "unpack" because they unpack a piece of data from the start of a stream

import struct

def unpackstruct(fmt, data):
  # decodes a chunk using the struct package
  size = struct.calcsize(fmt)
  return struct.unpack(fmt, data[:size]), data[size:]

def unpackbytes(n, data):
  # take n bytes
  return data[:n], data[n:]

def unpack7bit(data):
  # 7bit encoding
  # returns an integer
  # each byte contributes 7 bits
  # and the high bit marks continuation
  # the first byte is the least significant
  n = 0
  shift = 0
  while data[0] & 128:
    n += (data[0] & 127) << shift
    data = data[1:]
    shift += 7
  n += (data[0] & 127) << shift
  data = data[1:]
  shift += 7
  return n, data