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

class DataSlice:
  # a slice of bytes
  # represented as a buffer and an offset
  
  def __init__(self, buf):
    self.buf = buf
    self.offset = 0
  
  def unpackbytes(self, n):
    # returns the first n bytes
    # and advances the offset
    data = self.buf[self.offset:self.offset + n]
    self.offset += n
    return data
  
  def unpackstruct(self, fmt):
    # decode a chunk using the struct package
    return struct.unpack(fmt, self.unpackbytes(struct.calcsize(fmt)))
  
  def unpackbyte(self):
    # returns the first byte as an integer
    return self.unpackbytes(1)[0]
  
  def unpack7bit(self):
    # 7bit encoding
    # returns an integer
    # each byte contributes 7 bits
    # and the high bit marks continuation
    # the first byte is the least significant
    n = 0
    shift = 0
    b = 128 # so the loop goes at least one iteration
    while b & 128:
      b = self.unpackbyte()
      n += (b & 127) << shift
      shift += 7
    return n

  def unpackrest(self):
    # returns the rest of the buffer that's not consumed
    return self.unpackbytes(len(self.data) - self.offset)
