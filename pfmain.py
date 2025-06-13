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
    for substmt in block:
      if substmt[2][0] == 'fname' or 'impulsein' in pfnodes.getnode(substmt[2][1]):
        newsubstmts.append(substmt)
      else:
        datanodes.append(substmt)
    block[:] = newsubstmts
  walk2(code, f)
  return datanodes

def explicitimpulses1(code, varlist):
  # make linear nodes have explicit impulses
  vids = itertools.count()
  def f(block, path):
    for substmt1,substmt2 in zip(block, block[1:]):
      if substmt1[2][0] == 'name' and substmt1[2][1] != ['Impulse', 'Demultiplexer'] and not pfnodes.getnode(substmt1[2][1])['linear']:
        # may have multiple outputs
        # and will either have subblocks or explicit continuations
        continue
      assert len(substmt1[5]) == 0, 'linear statement may not have subblocks'
      impulseout = [ret for ret in substmt1[1] if ret[2] == 'iname'] # impulse outputs from the first node
      impulsein = [arg for arg in substmt2[4] if arg[0] == 'var' and arg[2] == 'iname'] # impulse inputs into the second node
      assert (len(impulseout) == 0) == (len(impulsein) == 0), f'two adjacent statements must both have either implicit or explicit impulses: {substmt1}, {substmt2}'
      if len(impulseout) == 0:
        # both implicit
        # add a new variable to the variable list
        var = ['var', ('il', next(vids)), 'iname']
        varlist.append(var)
        substmt1[1].insert(0, var)
        if substmt2[2][0] != 'name' or pfnodes.getnode(substmt2[2][1])['impulsein']:
          # the second statement takes impulse inputs
          substmt2[4].insert(0, var)
  walk2(code, f)

def explicitvaluejoin(code):
  # handle return in if and impulse multiplexer
  # not doing this rn tbh
  return
  vids = itertools.count()
  def f(block, path):
    newblock = []
    for substmt in block:
      newblock.append(substmt)
      if substmt[2] not in [['name', ['If']], ['name', ['Impulse', 'Multiplexer']]]:
        continue
      impulseout = [ret for ret in substmt[1] if ret[2] == 'iname'] # impulse outputs
      valout = [ret for ret in substmt[1] if ret[2] == 'name']
      if len(impulseout) != 0:
        assert len(substmt[5]) == 0, f'statement with explicit impulses may not have subblocks: {substmt}'
        assert len(valout) == 0, f'if/impulse multiplexer statement with explicit impulses may not return a value: {substmt}'
        continue
      # empty return will cause an error
      # also no early return :/
      if len(valout) == 0:
        continue
      assert False, 'return from if or impulse multiplexer not supported :('
      # force all branches to exist
      if substmt[2] == ['name', ['If']]:
        assert sorted([subblock[0] for subblock in substmt[5]]) == [['name', ['OnFalse']], ['name', ['OnTrue']]], 'if statement returning values must contain both branches'
        falsebranch = [subblock[1] for subblock in substmt[5] if subblock[0] == ['name', ['OnFalse']]][0]
        truebranch = [subblock[1] for subblock in substmt[5] if subblock[0] == ['name', ['OnTrue']]][0]
        falsereturn = falsebranch.pop()
        truereturn = truebranch.pop()
        assert falsereturn[2] == ['name', ['Return']], f'if statement returning values missing Return on false branch: {falsebranch}'
        assert truereturn[2] == ['name', ['Return']], f'if statement returning values missing Return on true branch: {truebranch}'
        assert falsereturn[1] == [], f'Return does not return a value (confusing, i know): {falsereturn}'
        assert truereturn[1] == [], f'Return does not return a value (confusing, i know): {truereturn}'
        assert falsereturn[3] == None, f'Return does not have a tag: {falsereturn}'
        trueretvals = truereturn[4]
        falseretvals = falsereturn[4]
        assert truereturn[3] == None, f'Return does not have a tag: {truereturn}'
        assert falsereturn[5] == [], f'Return does not have subblocks: {falsereturn}'
        assert truereturn[5] == [], f'Return does not have subblocks: {truereturn}'
        assert len(falseretvals) == len(valout), f'Return must have as many arguments as values returned from If: {falsereturn}'
        assert len(trueretvals) == len(valout), f'Return must have as many arguments as values returned from If: {truereturn}'
        for v,tv,fv in zip(valout, truereturn, falsereturn):
          # i'm assuming the value of the condition doesn't change during the execution :/
          newblock.append(['stmt', [v], ['name', ['Conditional']], None, [tv, fv, substmt[4][0]], []])
      else:
        assert sorted([subblock[0] for subblock in substmt[5]]) == [['literal', 'int', i] for i in range(len(substmt[5]))], 'impulse multiplexer statement returning values must contain all branches'
        branches = [[subblock[1] for subblock in substmt[5] if subblock[0] == ['literal', 'int', i]][0] for i in range(len(substmt[5]))]
        for i,branch in enumerate(branches):
          assert branch[-1][2] == ['name', ['Return']], f'impulse multiplexer statement returning values missing Return on branch {i}: {branch}'
        assert False, 'Impulse Multiplexer return not supported yet :('
    block[:] = newblock
  walk2(code, f)

def explicitimpulses2(code, varlist):
  # make branched nodes have explicit impulses
  # the ones with multiple impulses out, or with subblocks
  vids = itertools.count()
  def f(code):
    newcode = []
    for substmt in code:
      newcode.append(substmt)
      if substmt[2][0] == 'name' and substmt[2][1] != ['Impulse', 'Demultiplexer'] and not pfnodes.getnode(substmt[2][1])['linear']:
        # may have multiple outputs
        # and will either have subblocks or explicit continuations
        impulseout = [ret for ret in substmt[1] if ret[2] == 'iname'] # impulse outputs
        if len(impulseout) != 0:
          # has explicit impulses, not handled here
          continue
        blocks = substmt[5]
        blocks = [[name, f(block)] for _,name,block in blocks]
        invars = [] # going into the blocks
        outvars = [] # going out of the blocks
        for name,connectout in pfnodes.getnode(substmt[2][1])['impulseout']:
          if ['name', [name]] in [name for name,block in blocks]:
            block = [block for bname,block in blocks if bname == ['name', [name]]][0]
          else:
            block = []
          var = ['var', ('ib', next(vids)), 'iname']
          varlist.append(var)
          block.insert(0, ['stmt', [], ['name', ['Continue']], None, [var], []])
          invars.append(var)
          var = ['var', ('ic', next(vids)), 'iname']
          varlist.append(var)
          block.append(['stmt', [var], ['name', ['Continue']], None, [], []])
          if connectout:
            outvars.append(var)
          newcode += block
        substmt[5] = []
        substmt[1] = invars + substmt[1]
        if len(outvars) > 0:
          var = ['var', ('ij', next(vids)), 'iname']
          varlist.append(var)
          newcode.append(['stmt', [var], ['name', ['Join']], None, outvars, []])
    return newcode
  return f(code)

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

for fdef in functions.values():
  args,code = fdef
  vars_ = pfc.findvars(code)
  argvars = [['var', i - len(args), 'name'] for i in range(len(args))]
  vars_[(-1,)] = argvars
  pfc.resolvevars(code, vars_)
  datanodes = stripdatanodes(code)
  varlist = [v for vs in vars_.values() for n,v in vs]
  code = explicitimpulses2(code, varlist)
  explicitimpulses1(code, varlist)
  #explicitvaluejoin(code)
  fdef.pop(0) # remove the arguments (they're in the variable list now)
  fdef[0] = code + datanodes
  fdef.append(varlist)