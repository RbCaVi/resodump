import itertools

import pft
import pfc

#pprint.pprint(code)

def w(ss):
  for s in ss:
    if s[0] == 'stmt':
      for subblock in s[5]:
        w(subblock[2])
    else:
      print(s)

#w(code)

# def findfuncs(code):
#   funcs = []
#   def f(stmt, path):
#     funcs.append(stmt[2])
#   pfc.walk(code, f)
#   return funcs
#
# funcs = findfuncs(code)
#
# ufuncs = [fn for fn,_ in itertools.groupby(sorted(funcs))]

def walk2(code, f):
  # apply the function to code blocks instead of statements
  f(code, ())
  def f2(stmt, path):
    for i,subblock in enumerate(stmt[5]):
      f(subblock[2], path + (i,))
  pfc.walk(code, f2)

def stripfunctions(code):
  # strip out function definitions
  # won't catch nested function definitions :(
  functions = []
  def f(block, path):
    newsubstmts = []
    for substmt in block:
      if substmt[2] == ['name', ['Function']]:
        assert substmt[1] == [], 'Function does not return values'
        assert substmt[3] == None, 'Function does not have a tag'
        funcargs = substmt[4]
        assert all(arg[0] == 'name' for arg in funcargs), f'non name(s) found in argument list: {[arg for arg in funcargs if arg[0] == "name"]}'
        assert len(substmt[5]) == 1, 'Function should have one subblock'
        assert substmt[5][0][0] == 'subblock'
        assert substmt[5][0][1][0] == 'name'
        funcname = tuple(substmt[5][0][1][1])
        funccode = substmt[5][0][2]
        functions.append((funcname, funcargs, funccode))
      else:
        newsubstmts.append(substmt)
    block[:] = newsubstmts
  walk2(code, f)
  return functions

import pfnodes

def stripdatanodes(code):
  # strip out all data nodes
  datanodes = []
  def f(block, path):
    newsubstmts = []
    for substmt in block[:]:
      if substmt[2][0] == 'fname' or 'impulses' in pfnodes.getnode(substmt[2][1]):
        newsubstmts.append(substmt)
      else:
        datanodes.append(substmt)
    block[:] = newsubstmts
  walk2(code, f)
  return datanodes

with open('l.pft') as f:
  s = f.read()

import pprint

code = pft.parse(s)

funcdefs = stripfunctions(code)

functions = {}

for funcname,funcargs,funccode in funcdefs:
  assert funcname not in functions, f'duplicate function definition: {funcname}'
  functions[funcname] = [funcargs, funccode]

functions[()] = [[], code]

def explicitimpulses1(code, varlist):
  # make linear nodes have explicit impulses
  vids = itertools.count()
  def f(block, path):
    for substmt1,substmt2 in zip(block, block[1:]):
      if pfnodes.getnode(substmt2[2][1])['impulses'] != True:
        # may have multiple outputs
        continue
      impulseout = [ret for ret in substmt1[1] if ret[2] == 'iname'] # impulse outputs from the first node
      impulsein = [arg for arg in substmt2[4] if arg[0] == 'var' and arg[2] == 'iname'] # impulse inputs into the second node
      assert (len(impulseout) == 0) == (len(impulsein) == 0), f'two adjacent statements must both have either implicit or explicit impulses: {substmt1}, {substmt2}'
      if len(impulseout) == 0:
        # both implicit
        # add a new variable to the variable list
        var = ['var', ('i1', next(vids)), 'iname']
        varlist.append(var)
        substmt1[1].insert(0, var)
        substmt2[4].insert(0, var)
  walk2(code, f)

for fdef in functions.values():
  args,code = fdef
  vars_ = pfc.findvars(code)
  argvars = [['var', i - len(args), 'name'] for i in range(len(args))]
  vars_[(-1,)] = argvars
  pfc.resolvevars(code, vars_)
  datanodes = stripdatanodes(code)
  varlist = [v for vs in vars_.values() for n,v in vs]
  explicitimpulses1(code, varlist)
  fdef.pop(0) # remove the arguments (they're in the variable list now)
  fdef.append(varlist)
  fdef.append(datanodes)