import itertools

import pft
import pfc

vids = itertools.count()

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
      if substmt[2][0] == 'fname' or 'impulsein' in pfnodes.getnode(substmt[2][1]) or substmt[2][1] == ['Return'] or substmt[2][1] == ['Impulse', 'Demultiplexer'] or substmt[2][1] == ['Join']:
        newsubstmts.append(substmt)
      else:
        datanodes.append(substmt)
    block[:] = newsubstmts
  walk2(code, f)
  return datanodes

def addlinearimpulses(code, varlist):
  # make linear nodes (one impulse in, one impulse out) have explicit impulses
  def f(block, path):
    for substmt1,substmt2 in zip(block, block[1:]):
      if substmt1[2][0] == 'name' and substmt1[2][1] != ['Impulse', 'Demultiplexer'] and substmt1[2][1] != ['Join'] and not pfnodes.getnode(substmt1[2][1])['linear']:
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

def flattenbranches(code, varlist):
  # make branched nodes have explicit impulses
  # the ones with multiple impulses out, or with subblocks
  def f(code):
    newcode = []
    for substmt in code:
      newcode.append(substmt)
      if substmt[2][0] == 'name' and substmt[2][1] != ['Impulse', 'Demultiplexer'] and substmt[2][1] != ['Join'] and not pfnodes.getnode(substmt[2][1])['linear']:
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
          newcode.append(['stmt', [], ['name', ['Join']], None, outvars, []])
    return newcode
  return f(code)

def filter2(f, l):
  # split a list into 2 lists
  # the first one when the predicate is true
  # and the second one when the predicate is false
  l1 = []
  l2 = []
  for x in l:
    if f(x):
      l1.append(x)
    else:
      l2.append(x)
  return l1, l2

def reformatstmt(stmt):
  # reformat the statement
  # the order of the parts is the same as in source code
  # reordered to name tag args returns
  # with args and returns split into impulses and not impulses
  _,rets,name,tag,args,subblocks = stmt
  assert len(subblocks) == 0, f'there\'s not supposed to be a subblock here: {stmt}'
  argsi,argsv = filter2(lambda arg: arg[0] == 'var' and arg[2] == 'iname', args)
  retsi,retsv = filter2(lambda ret: ret[2] == 'iname', rets) # returns are (i hope) always variables
  return [name, tag, argsi, argsv, retsi, retsv]

def renameimpulse(code, pat, repl):
  for stmt in code:
    stmt[2] = [repl if v == pat else v for v in stmt[2]]
    stmt[4] = [repl if v == pat else v for v in stmt[4]]

def renamevar(code, pat, repl):
  for stmt in code:
    stmt[3] = [repl if v == pat else v for v in stmt[3]]
    stmt[5] = [repl if v == pat else v for v in stmt[5]]

def removejoins(code, varlist):
  # also removes continues :)
  # i could just say continue is join one input
  # but that would mean i have to special case it for addlinearimpulses()
  for stmt in code:
    if stmt[0] not in [['name', ['Join']], ['name', ['Continue']]]:
      continue
    name,tag,argsi,argsv,retsi,retsv = stmt
    assert tag is None, f'Join or Continue cannot have a tag: {stmt}'
    assert len(argsv) == 0, f'Join or Continue cannot have value arguments: {stmt}'
    assert len(retsv) == 0, f'Join or Continue cannot return values: {stmt}'
    if name == ['name', ['Continue']]:
      assert len(argsi) == 1, f'Continue must have one impulse input: {stmt}'
    assert len(retsi) == 1, f'Join or Continue cannot have more than one impulse output: {stmt}'
    for arg in argsi:
      renameimpulse(code, arg, retsi[0])
  code = [s for s in code if s[0] not in [['name', ['Join']], ['name', ['Continue']]]]
  return code

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
  #explicitvaluejoin(code)
  code = flattenbranches(code, varlist)
  if code[-1][2] == ['name', ['Return']]:
    var = ['var', 'ie', 'iname'] # this will be stripped by removejoins(), but it'll leave an impulse input on the first statement for an entry point
    varlist.append(var)
    code.insert(0, ['stmt', [], ['name', ['Continue']], None, [var], []])
    reti = len(code) - 1
  else:
    reti = None
  addlinearimpulses(code, varlist)
  code += datanodes # code is now a list of nodes with no nesting
  code = [reformatstmt(s) for s in code]
  if reti is not None: # don't do drugs, kids
    ret = code[reti]
  else:
    ret = None
  code = removejoins(code, varlist)
  fdef.pop(0) # remove the arguments (they're in the variable list now)
  fdef[0] = code
  fdef.append(varlist)
  fdef.append(argvars)
  fdef.append(ret)

# functions is now a dict of name to [func code, variables]

# now inline them into each other

funcdeps = {}

for name,(code,varlist,args,ret) in functions.items():
  funcdeps[name] = {tuple(n) for (t,n),*_ in code if t == 'fname'}

# i could remove unused functions
# but not today

funcnames = {*functions}
sortedfuncs = []

for i in range(len(funcnames)):
  for name in funcnames:
    if all(dep not in funcnames for dep in funcdeps[name]):
      sortedfuncs.append(name)
      funcnames.remove(name)
      break
  else:
    assert False, 'recursive or undefined function detected, aborting'

calls = {name:[] for name in functions}
for name,(code,varlist,args,ret) in functions.items():
  # renumber the variables
  # to avoid collision
  for var in varlist:
    var[1] = next(vids)
  # collect all calls
  for stmt in code:
    name,tag,argsi,argsv,retsi,retsv = stmt
    if name[0] == 'fname':
      assert tag is None, 'user defined functions can\'t have a tag'
      assert len(argsi) == 1, 'user defined functions must have linear control flow'
      assert len(retsi) == 1, 'user defined functions must have linear control flow'
      calls[tuple(name[1])].append([argsi[0], retsi[0], argsv, retsv])

assert calls[()] == [], 'main code should not be called (or callable for that matter)'
del calls[()]

finalcode = sum([[stmt for stmt in code if stmt[0][0] != 'fname'] for code,varlist,args,ret in functions.values()], [])
varlist = sum([varlist for code,varlist,args,ret in functions.values()], [])

for name,fcalls in calls.items():
  ret = functions[name][3]
  assert ret is not None, 'function must have return'
  argi = functions[name][0][0][2][0]
  reti = ret[2][0]
  args = functions[name][2]
  rets = ret[3]
  argis,retis,argvs,retvs = zip(*fcalls, strict = True)
  argvs = [*zip(*argvs, strict = True)]
  retvs = [*zip(*retvs, strict = True)]
  var = ['var', ('if', next(vids)), 'name']
  varlist.append(var)
  finalcode.append([['name', ['Impulse', 'Demultiplexer']], None, [*argis], [], [argi], [var]])
  finalcode.append([['name', ['Impulse', 'Multiplexer']], None, [reti], [var], [*retis], []])
  for arg,argv in zip(args, argvs):
    finalcode.append([['name', ['Multiplex']], None, [], [var, *argv], [], [arg]])
  for ret,retv in zip(rets, retvs):
    for rv in retv:
      renamevar(finalcode, rv, ret)

finalcode = [s for s in finalcode if s[0] not in [['name', ['Return']]]]

ivars = []
vvars = []

for var in varlist:
  argcount = 0
  retcount = 0
  for stmt in finalcode:
    name,tag,argsi,argsv,retsi,retsv = stmt
    if var in argsi + argsv:
      argcount += 1
    if var in retsi + retsv:
      retcount += 1
  if var[2] == 'name':
    if retcount == 0:
      assert argcount == 0, 'an undefined variable cannot be used'
      continue
    assert retcount == 1, 'a variable can only be defined once'
    vvars.append(var)
  else:
    if argcount == 0:
      continue
    assert argcount == 1, 'an impulse (possibly joined) can only be used once'
    ivars.append(var)

ivarlocs = {}

for ivar in ivars:
  ivarlocs[tuple(ivar)] = [i for i,s in enumerate(finalcode) if ivar in s[2]][0]

vvarlocs = {}

for vvar in vvars:
  vvarlocs[tuple(vvar)] = [i for i,s in enumerate(finalcode) if vvar in s[5]][0]

ivaruses = {tuple(ivar):[] for ivar in ivars} # actually the places that generate the impulses because they have reverse dependency
vvaruses = {tuple(vvar):[] for vvar in vvars}

for i,stmt in enumerate(finalcode):
  for i2,ivar in enumerate(stmt[4]):
    if tuple(ivar) in ivaruses: # if the impulse is ever used
      ivaruses[tuple(ivar)].append([i, i2])
  for vvar in stmt[3]:
    if vvar in vvars: # if it's actually a variable
      vvaruses[tuple(vvar)].append([i, i2])

#pprint.pprint(finalcode)
#pprint.pprint(ivars)
#pprint.pprint(vvars)
#pprint.pprint(ivarlocs)
#pprint.pprint(vvarlocs)
#pprint.pprint(ivaruses)
#pprint.pprint(vvaruses)

if False: # print a graph representation for graphonline.top
  for i,stmt in enumerate(finalcode):
    name,tag,argsi,argsv,retsi,retsv = stmt
    n = f'{i} {name} {tag}'
    for ai in argsi:
      print(f'{ai}>{n}')
    for av in argsv:
      print(f'{av}>{n}')
    for ri in retsi:
      print(f'{n}>{ri}')
    for rv in retsv:
      print(f'{n}>{rv}')

if False: # toposort nodes and print out code (but joined impulses aren't handled...)
  deps = {i:set() for i in range(len(finalcode))}

  for ivar in ivars:
    for x in ivaruses[tuple(ivar)]:
      deps[ivarlocs[tuple(ivar)]].add(x)

  for vvar in vvars:
    for x in vvaruses[tuple(vvar)]:
      deps[x].add(vvarlocs[tuple(vvar)])

  nodes = {*deps.keys()}
  sortednodes = []

  for i in range(len(nodes)):
    for name in nodes:
      if all(dep not in nodes for dep in deps[name]):
        sortednodes.append(name)
        nodes.remove(name)
        break
    else:
      assert False, 'recursive or undefined function detected, aborting'

  ivids = itertools.count()
  vvids = itertools.count()
  for var in varlist:
    if var[2] == 'iname':
      var[1] = next(ivids)
    else:
      var[1] = next(vvids)

  sortednodes = [finalcode[i] for i in sortednodes]

  def render(t):
    if t[0] == 'name':
      return ' '.join(t[1])
    if t[0] == 'var':
      if t[2] == 'iname':
        return f'@i{t[1]}'
      if t[2] == 'name':
        return f'v{t[1]}'
    if t[0] == 'literal':
      if t[1] == 'string':
        return f'"{t[2]}"'
      if t[1] == 'int':
        return f'{t[2]}'
      if t[1] == 'rname':
        return '[[' + ' '.join(t[2]) + ']]'
      if t[1] == 'BodyNode':
        return f'{t[2]}'
      if t[1] == 'bool':
        return 'true' if t[2] else 'false'
      if t[1] == 'array':
        return '[' + ', '.join(render(['literal', *x]) for x in t[2]) + ']'
      if t[1] == 'null':
        return 'null'
      if t[1] == 'float':
        return f'{t[2]}'
    assert False, t

  for node in sortednodes:
    name,tag,argsi,argsv,retsi,retsv = node
    name = render(name)
    if tag is not None:
      name += ' <' + render(tag) + '>'
    args = [render(arg) for arg in argsi] + [render(arg) for arg in argsv]
    rets = [render(ret) for ret in retsi] + [render(ret) for ret in retsv]
    if len(rets) > 0:
      name = ','.join(rets) + ' = ' + name
    name += ' (' + ', '.join(args) + ')'
    print(name)

for 


