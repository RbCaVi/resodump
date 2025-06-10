import pft
import pfc

with open('l.pft') as f:
  s = f.read()

import pprint

parsed = parse(s)

pprint.pprint(parsed)

def w(ss):
  for s in ss:
    if s[0] == 'stmt':
      for subblock in s[5]:
        w(subblock[2])
    else:
      print(s)

w(parsed)