# lz4 compression used by resonite
# open source on github at https://github.com/MiloszKrajewski/lz4net
# taken from resonite LZ4.dll
# through dotpeek

# the lz4 stream format is composed of a series of chunks
# a chunk is:
#   flags - 7bit encoded
#     1 - is compressed
#   uncompressed length - 7bit encoded
#   if compressed:
#     compressed length - 7bit encoded
#     data - <compressed length> bytes - decompressed by LZ4_uncompress_safe32()
#   otherwise:
#     data - <uncompressed length> bytes - passed straight to output

# compressed data is also made of a series of chunks
# a chunk is:
#   copy length 1 and copy length 2 - 1 byte - high 4 bits and low 4 bits respectively
#   extra length 1 - if copy length 1 is 15 - series of 255 bytes and one more, added to copy length 1
#   literal - <copy length 1> bytes - passed straight to output
#   backreference offset - 2 byte int
#   extra length 2 - like extra length 1
#   it then copies 4 bytes to the end, maybe moves the backreference pointer back a few bytes, and copies <extra length 2> bytes to the end

import struct
import io

import unpack

def unpack255len(data):
  # start with n = 15 because that's the condition
  # read any number of 255's and one non 255 byte
  # and sum them to get a length
  n = 15
  ni = 255
  while ni == 255:
    ni = unpack.unpackbyte(data)
    n += ni
  return n

# this is from https://github.com/MiloszKrajewski/lz4net/blob/master/src/LZ4ps/LZ4Codec.Safe32.Dirty.cs
# and https://github.com/MiloszKrajewski/lz4net/blob/master/src/LZ4ps/LZ4Codec.Safe.cs
# the function names and structure matched, so it's probably the same
# i also peeled off a lot of stuff
# few "unnecessary" branches (they did the same things in both branches)
# minor fix to wildcopy() (it would return 0 if less than 16 bytes were copied) before folding it into blockcopy()
# also folded copy4() into securecopy() (it was only used when source and destination did not overlap)

def securecopy(buf, src_p, count):
  # copy a range of bytes from `buf[src_p:src_p + count]` to the end of buf
  # if `src_p + count` is past the current end of `buf`, it will
  # repeat the chunk from `src_p` to the end of `buf`
  # this is relevant to the decompression
  # this function is equivalent to a copy starting from src_p without any overlap checking
  if count > 0:
    chunk = buf[src_p:]
    return (chunk * ((count // len(chunk)) + 1))[:count]
  return b''

def blockcopy(src, count):
  # copy bytes by count
  return unpack.unpackbytes(count, src)

COPYLENGTH = 8
DECODER_TABLE_32 = [0, 3, 2, 3]
LASTLITERALS = 5

class LZ4ChunkStream:
  def __init__(self, src, length):
    self.buf = bytearray(length)
    self.woff = 0
    self.roff = 0
    self.it = LZ4_uncompress_safe32(src, self, length)
    self.sentinel = object()
  
  def append(self, data):
    l = len(data)
    self.buf[self.woff:self.woff + l] = data
    self.woff += l
    return data
  
  def securecopy(self, start, count):
    # start is always negative
    chunk = self.buf[self.woff + start:self.woff]
    return (chunk * ((count // len(chunk)) + 1))[:count]
  
  def read(self, size):
    end = self.roff + size
    while self.woff < end:
      chunk = next(self.it, self.sentinel)
      if chunk == self.sentinel:
        end = self.woff
      else:
        self.append(chunk)
    data = self.buf[self.roff:end]
    self.roff = end
    return data

def LZ4_uncompress_safe32(src, dst, dst_len):
  while True:
    lengths = unpack.unpackbyte(src)
    length1 = lengths >> 4
    if length1 == 15:
      length1 = unpack255len(src)
    yield blockcopy(src, length1)
    if dst.woff > dst_len - COPYLENGTH:
      assert unpack.isempty(src), 'unconsumed input'
      assert dst.woff == len(dst.buf), 'unclean end'
      return
    backoffset, = unpack.unpackstruct('<H', src)
    assert backoffset <= dst.woff, 'backreference underflow'
    dst_ref = -backoffset
    length2 = lengths & 15
    if length2 == 15:
      length2 = unpack255len(src)
    yield dst.securecopy(dst_ref, 4)
    if backoffset < 4:
      dst_ref -= DECODER_TABLE_32[backoffset]
    yield dst.securecopy(dst_ref, length2)
    assert dst.woff <= dst_len - LASTLITERALS, 'not enough space for more literals'

class ChainStream:
  # convert an iterator of streams with .read() into a stream with only .read()
  def __init__(self, it):
    # it is an iterable of bytes
    self.it = it
    self.buf = next(self.it)
    self.sentinel = object()
  
  def read(self, size):
    out = b''
    while size > 0:
      chunk = self.buf.read(size)
      size -= len(chunk)
      out += chunk
      if len(chunk) == 0:
        buf = next(self.it, self.sentinel)
        if buf == self.sentinel:
          break
        self.buf = buf
    return out

class StreamSlice:
  # the first size bytes of a stream
  # make sure you use all of them before using the original stream again
  def __init__(self, stream, size):
    self.stream = stream
    self.size = size
    self.off = 0
  
  def read(self, size):
    if self.off + size > self.size:
      size = self.size - self.off
    self.off += size
    return self.stream.read(size)

# this is mostly LZ4Stream::AcquireNextChunk()
# then i concatenate all the chunks together
def lz4decompressstream(data):
  while True:
    if unpack.isempty(data):
      return
    flags = unpack.unpack7bit(data)
    flag = bool(flags & 1)
    l1 = unpack.unpack7bit(data)
    if not flag:
      yield io.BytesIO(unpack.unpackbytes(l1, data))
    else:
      l2 = unpack.unpack7bit(data)
      if l2 > l1:
        assert False, 'invalid size? - compressed data is not compressed :('
      chunk = StreamSlice(data, l2)
      yield LZ4ChunkStream(chunk, l1)

def lz4decompress(data):
  return ChainStream(lz4decompressstream(data))

def LZ4_uncompress_safe32_start(src, dst_len, n):
  dst = b''
  while True:
    if len(dst) > n:
      return dst
    lengths = unpack.unpackbyte(src)
    length1 = lengths >> 4
    if length1 == 15:
      length1 = unpack255len(src)
    dst += blockcopy(src, length1)
    if len(dst) > dst_len - COPYLENGTH:
      assert len(dst) == dst_len, 'unclean end'
      assert len(src) == 0, 'unconsumed input'
      return dst
    (backoffset,) = unpack.unpackstruct('<H', src)
    assert backoffset <= len(dst), 'backreference underflow'
    dst_ref = -backoffset
    length2 = lengths & 15
    if length2 == 15:
      length2 = unpack255len(src)
    dst += securecopy(dst, dst_ref, 4)
    if backoffset < 4:
      dst_ref -= DECODER_TABLE_32[backoffset]
    dst += securecopy(dst, dst_ref, length2)
    assert len(dst) <= dst_len - LASTLITERALS, 'not enough space for more literals'

# attempt to decompress only `n` bytes
# for detecting meshx
def lz4decompressstart(data, n):
  decompressed = b''
  while True:
    if len(decompressed) > n:
      return decompressed
    if len(data) == 0:
      return decompressed
    flags = unpack.unpack7bit(data)
    flag = bool(flags & 1)
    l1 = unpack.unpack7bit(data)
    if not flag:
      chunk = unpack.unpackbytes(min(l1, 6), data)
    else:
      l2 = unpack.unpack7bit(data)
      if l2 > l1:
        assert False, 'invalid size? - compressed data is not compressed :('
      chunk = unpack.unpackbytes(l2, data)
      chunk = LZ4_uncompress_safe32_start(chunk, l1, n)
    decompressed += chunk