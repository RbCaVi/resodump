import itertools

import pft
import pfc

with open('l.pft') as f:
  s = f.read()

import pprint

code = pft.parse(s)

#pprint.pprint(code)

def w(ss):
  for s in ss:
    if s[0] == 'stmt':
      for subblock in s[5]:
        w(subblock[2])
    else:
      print(s)

#w(code)

vars_ = pfc.findvars(code)

pfc.resolvevars(code, vars_)

pprint.pprint(code)

def findfuncs(code):
  funcs = []
  def f(stmt, path):
    funcs.append(stmt[2])
  pfc.walk(code, f)
  return funcs

funcs = findfuncs(code)

ufuncs = [fn for fn,_ in itertools.groupby(sorted(funcs))]