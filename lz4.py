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

import unpack

def unpack255len(data):
  # start with n = 15 because that's the condition
  # read any number of 255's and one non 255 byte
  # and sum them to get a length
  offset = 0
  n = 15
  while True:
    ni = data[offset]
    offset += 1
    n += ni
    if ni != 255:
      return n, data[offset:]

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
    buf += (chunk * ((count // len(chunk)) + 1))[:count]
  return buf

def blockcopy(src, dst, count):
  # copy bytes by count
  return dst + src[:count], src[count:]

COPYLENGTH = 8
DECODER_TABLE_32 = [0, 3, 2, 3]
LASTLITERALS = 5

def LZ4_uncompress_safe32(src, dst_len):
  dst = b''
  while True:
    (lengths,),src = unpack.unpackbytes(1, src)
    length1 = lengths >> 4
    if length1 == 15:
      length1,src = unpack255len(src)
    dst,src = blockcopy(src, dst, length1)
    if len(dst) > dst_len - COPYLENGTH:
      assert len(dst) == dst_len, 'unclean end'
      assert len(src) == 0, 'unconsumed input'
      return dst
    (backoffset,),src = unpack.unpackstruct('<H', src)
    assert backoffset <= len(dst), 'backreference underflow'
    dst_ref = -backoffset
    length2 = lengths & 15
    if length2 == 15:
      length2,src = unpack255len(src)
    dst = securecopy(dst, dst_ref, 4)
    if backoffset < 4:
      dst_ref -= DECODER_TABLE_32[backoffset]
    dst = securecopy(dst, dst_ref, length2)
    assert len(dst) <= dst_len - LASTLITERALS, 'not enough space for more literals'

# this is mostly LZ4Stream::AcquireNextChunk()
# then i concatenate all the chunks together
def lz4decompress(data):
  decompressed = b''
  while True:
    if len(data) == 0:
      return decompressed
    flags,data = unpack.unpack7bit(data)
    flag = bool(flags & 1)
    l1,data = unpack.unpack7bit(data)
    if not flag:
      chunk,data = unpack.unpackbytes(l1, data)
    else:
      l2,data = unpack.unpack7bit(data)
      if l2 > l1:
        assert False, 'invalid size? - compressed data is not compressed :('
      chunk,data = unpack.unpackbytes(l2, data)
      chunk = LZ4_uncompress_safe32(chunk, l1)
    decompressed += chunk

def LZ4_uncompress_safe32_start(src, dst_len, n):
  dst = b''
  while True:
    if len(dst) > n:
      return dst
    (lengths,),src = unpack.unpackbytes(1, src)
    length1 = lengths >> 4
    if length1 == 15:
      length1,src = unpack255len(src)
    dst,src = blockcopy(src, dst, length1)
    if len(dst) > dst_len - COPYLENGTH:
      assert len(dst) == dst_len, 'unclean end'
      assert len(src) == 0, 'unconsumed input'
      return dst
    (backoffset,),src = unpack.unpackstruct('<H', src)
    assert backoffset <= len(dst), 'backreference underflow'
    dst_ref = -backoffset
    length2 = lengths & 15
    if length2 == 15:
      length2,src = unpack255len(src)
    dst = securecopy(dst, dst_ref, 4)
    if backoffset < 4:
      dst_ref -= DECODER_TABLE_32[backoffset]
    dst = securecopy(dst, dst_ref, length2)
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
    flags,data = unpack.unpack7bit(data)
    flag = bool(flags & 1)
    l1,data = unpack.unpack7bit(data)
    if not flag:
      chunk,data = unpack.unpackbytes(min(l1, 6), data)
    else:
      l2,data = unpack.unpack7bit(data)
      if l2 > l1:
        assert False, 'invalid size? - compressed data is not compressed :('
      chunk,data = unpack.unpackbytes(l2, data)
      chunk = LZ4_uncompress_safe32_start(chunk, l1, n)
    decompressed += chunk