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

def findfuncs(code):
  funcs = []
  def f(stmt, path):
    funcs.append(stmt[2])
  pfc.walk(code, f)
  return funcs

funcs = findfuncs(code)

ufuncs = [fn for fn,_ in itertools.groupby(sorted(funcs))]

import pfnodes

def stripdatanodes(code):
  # strip out all data nodes
  datanodes = []
  def f(stmt, path):
    for subblock in stmt[5]:
      newsubstmts = []
      for substmt in subblock[2]:
        if substmt[2][0] == 'fname' or 'continuations' in pfnodes.getnode(substmt[2][1]):
          newsubstmts.append(substmt)
        else:
          datanodes.append(substmt)
      subblock[2] = newsubstmts
  pfc.walk(code, f)
  newcode = []
  for stmt in code:
    if stmt[2][0] == 'fname' or 'continuations' in pfnodes.getnode(stmt[2][1]):
      newcode.append(stmt)
    else:
      datanodes.append(stmt)
  code[:] = newcode
  return datanodes

datanodes = stripdatanodes(code)