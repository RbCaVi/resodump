import itertools
import functools
import re

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
    for i,subblock in enumerate(stmt[6]):
      f(subblock[1], path + (i,))
  pfc.walk(code, f2)

def stripfunctions(code):
  # strip out function definitions
  # won't catch nested function definitions :/
  functions = []
  def f(block, path):
    newsubstmts = []
    for substmt in block:
      if substmt[0] == ['name', ('Function',)]:
        assert len(substmt[4]) == 0, 'Function does not return impulses'
        assert len(substmt[5]) == 0, 'Function does not return values'
        assert substmt[1] == None, 'Function does not have a tag'
        assert len(substmt[2]) == 0, 'Function does not take impulses'
        funcargs = substmt[3]
        assert len(substmt[6]) == 1, 'Function should have one subblock'
        subblock = substmt[6][0]
        assert subblock[0][0] == 'name'
        funcname = tuple(subblock[0][1])
        funccode = subblock[1]
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
      if substmt[0][0] == 'fname' or 'impulsein' in pfnodes.getnode(substmt[0][1]) or substmt[0][1] == ('Return',) or substmt[0][1] == ('Impulse', 'Demultiplexer') or substmt[0][1] == ('Join',):
        newsubstmts.append(substmt)
      else:
        datanodes.append(substmt[:6])
    block[:] = newsubstmts
  walk2(code, f)
  return datanodes

def addlinearimpulses(code, ivarlist):
  # make linear nodes (one impulse in, one impulse out) have explicit impulses
  for substmt1,substmt2 in zip(code, code[1:]):
    if substmt1[0][0] == 'name' and substmt1[0][1] != ('Impulse', 'Demultiplexer') and substmt1[0][1] != ('Join',) and not pfnodes.getnode(substmt1[0][1])['linear']:
      # may have multiple outputs
      # and will either have subblocks or explicit continuations
      continue
    impulseout = substmt1[4] # impulse outputs from the first node
    impulsein = substmt2[2] # impulse inputs into the second node
    assert (len(impulseout) == 0) == (len(impulsein) == 0), f'two adjacent statements must both have either implicit or explicit impulses: {substmt1}, {substmt2}'
    if len(impulseout) == 0:
      # both implicit
      # add a new variable to the variable list
      var = ['var', ('il', next(vids))]
      ivarlist.append(var)
      substmt1[4].insert(0, var)
      if substmt2[0][0] != 'name' or pfnodes.getnode(substmt2[0][1])['impulsein']:
        # the second statement takes an impulse input
        substmt2[2].insert(0, var)
      else:
        print(substmt2[0], 'doesn\'t take an impulse in')

def flattenbranches(code, ivarlist):
  # make branched nodes have explicit impulses
  # the ones with multiple impulses out, or with subblocks
  def f(code):
    newcode = []
    for substmt in code:
      newcode.append(substmt)
      if substmt[0][0] == 'name' and substmt[0][1] != ('Impulse', 'Demultiplexer') and substmt[0][1] != ('Join',) and not pfnodes.getnode(substmt[0][1])['linear']:
        # may have multiple outputs
        # and will either have subblocks or explicit continuations
        if len(substmt[4]) != 0:
          # has explicit impulses, not handled here
          assert len(substmt[6]) == 0, 'statement with explicit impulse outputs may not also have subblocks'
          continue
        blocks = substmt[6]
        blocks = [[name, f(block)] for name,block in blocks]
        invars = [] # going into the blocks
        outvars = [] # going out of the blocks
        for name,connectout in pfnodes.getnode(substmt[0][1])['impulseout']:
          if ['name', (name,)] in [name for name,block in blocks]:
            block = [block for bname,block in blocks if bname == ['name', (name,)]][0]
          else:
            block = []
          var = ['var', ('ib', next(vids))]
          ivarlist.append(var)
          block.insert(0, [['name', ('Continue',)], None, [var], [], [], []])
          invars.append(var)
          var = ['var', ('ic', next(vids))]
          ivarlist.append(var)
          block.append([['name', ('Continue',)], None, [], [], [var], []])
          if connectout:
            outvars.append(var)
          newcode += block
        substmt[4] = invars
        if len(outvars) > 0:
          newcode.append([['name', ('Join',)], None, [outvars], [], [], []])
      substmt[6:] = []
    return newcode
  return f(code)

def renameimpulse(code, pat, repl):
  for stmt in code:
    stmt[2] = [repl if v == pat else v for v in stmt[2]]
    stmt[4] = [repl if v == pat else v for v in stmt[4]]

def renamevar(code, pat, repl):
  for stmt in code:
    stmt[3] = [repl if v == pat else v for v in stmt[3]]
    stmt[5] = [repl if v == pat else v for v in stmt[5]]

def removejoins(code):
  # also removes continues :)
  # i could just say continue is join one input
  # but that would mean i have to special case it for addlinearimpulses()
  for stmt in code:
    if stmt[0] not in [['name', ('Join',)], ['name', ('Continue',)]]:
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
  code = [s for s in code if s[0] not in [['name', ('Join',)], ['name', ('Continue',)]]]
  return code

# type inference

# can this type `t` cast to the union type `ts` represented as a set of type string identifiers?
def typeincluded(t, ts):
  if t in ts:
    return True
  if t == 'int' and 'float' in ts:
    return True
  if t == 'int2' and 'float2' in ts:
    return True
  if t == 'int3' and 'float3' in ts:
    return True
  if t == 'Grabber' and 'Component' in ts:
    return True
  if t == 'null' and 'string' in ts:
    return True
  return False

def intersecttypes2(t1, t2):
  if t1 == '$':
    return t2
  if t2 == '$':
    return t1
  ts = set()
  for t in t1:
    if typeincluded(t, t2):
      ts.add(t)
  for t in t2:
    if typeincluded(t, t1):
      ts.add(t)
  return ts

def intersecttypes(*ts):
  #print('ts pmo', ts, functools.reduce(intersecttypes2, ts))
  return functools.reduce(intersecttypes2, ts)

def uniontypes2(t1, t2):
  if t1 == '$':
    return '$'
  if t2 == '$':
    return '$'
  return t1 | t2

def uniontypes(*ts):
  return functools.reduce(uniontypes2, ts)

# this doesn't take into account the tag yet.....
def gettypes(nodedata, intypes, outtypes):
  if 'forms' in nodedata:
    # uh...
    # in and out
    intypes2,outtypes2 = zip(*[gettypes(form, intypes, outtypes) for form in nodedata['forms']])
    #print(nodedata)
    #print(intypes, outtypes, intypes2, outtypes2)
    intypes = [intersecttypes2(it, t) for it,t in zip(intypes, map(uniontypes, *intypes2))]
    outtypes = [intersecttypes2(it, t) for it,t in zip(outtypes, map(uniontypes, *outtypes2))]
    #print('yee', intypes, outtypes)
    return intypes, outtypes
  nodein = nodedata['in']
  nodeout = nodedata['out']
  if type(nodeout) == str:
    nodeout = [[nodeout, '*']]
  if len(nodein) == 1 and nodein[0][0] == '*$':
    nodein = [['$', None] for t in intypes]
  #if len(nodein) == 2 and nodein[1][0] == '*$': # special case for multiplex
  #  nodein = [modein[0]] + [['$', None] for t in intypes]
  if len(intypes) != len(nodein):
    return [set(['nope']) for _ in intypes], [set(['nope']) for _ in outtypes]
  if len(outtypes) != len(nodeout):
    return [set(['nope']) for _ in intypes], [set(['nope']) for _ in outtypes]
  # find $ as intersection of input and output $ types
  # you might be able to narrow the type of a non directly connected node
  # because inputs also change the type of the variables connected to them
  # so i can propagate the type backward to nodes with only generic outputs
  # like Read Dynamic Variable
  if '$' in [t for t,n in nodein] + [t for t,n in nodeout]:
    gtype = intersecttypes(*[it for it,(t,n) in zip(intypes, nodein) if t == '$'], *[ot for ot,(t,n) in zip(outtypes, nodeout) if t == '$'])
    #print(gtype, [it for it,(t,n) in zip(intypes, nodein) if t == '$'], [ot for ot,(t,n) in zip(outtypes, nodeout) if t == '$'])
  #print([[it, t, intersecttypes2(it, t)] for it,(t,n) in zip(intypes, nodein)], [[ot, t, intersecttypes2(ot, t)] for ot,(t,n) in zip(outtypes, nodeout)])
  if any(intersecttypes2(it, t) == set() for it,(t,n) in zip(intypes, nodein)) or any(intersecttypes2(ot, t) == set() for ot,(t,n) in zip(outtypes, nodeout)):
    return [set(['nope']) for _ in intypes], [set(['nope']) for _ in outtypes]
  return [gtype if t == '$' else {t} for t,n in nodein], [gtype if t == '$' else {t} for t,n in nodeout]

# not final
valuetypes = ['bool', 'float', 'int', 'BodyNode', 'int3']
objecttypes = ['string']
reftypes = ['Slot', 'Tool']
elementtypes = ['Tool']

# now for generation (?)
# casts might be an issue...
# eh
def choosenode(nodedata, intypes, outtypes):
  if 'forms' in nodedata:
    # uh...
    # in and out
    nodes = [choosenode(form, intypes, outtypes) for form in nodedata['forms']]
    nodes = [node for node in nodes if node is not None]
    if len(nodes) > 1:
      print(f"INFO: choosing one node of {nodes}")
    return nodes[0]
  nodein = nodedata['in']
  nodeout = nodedata['out']
  if type(nodeout) == str:
    nodeout = [[nodeout, '*']]
  if len(nodein) == 1 and nodein[0][0] == '*$':
    nodein = [['$', None] for t in intypes]
  if len(intypes) != len(nodein):
    return None
  if len(outtypes) != len(nodeout):
    return None
  # find $ as intersection of input and output $ types
  # you might be able to narrow the type of a non directly connected node
  # because inputs also change the type of the variables connected to them
  # so i can propagate the type backward to nodes with only generic outputs
  # like Read Dynamic Variable
  if '$' in [t for t,n in nodein] + [t for t,n in nodeout]:
    gtype = intersecttypes(*[it for it,(t,n) in zip(intypes, nodein) if t == '$'], *[ot for ot,(t,n) in zip(outtypes, nodeout) if t == '$'])
    #print(gtype, [it for it,(t,n) in zip(intypes, nodein) if t == '$'], [ot for ot,(t,n) in zip(outtypes, nodeout) if t == '$'])
    nodein = [(gtype if t == '$' else {t}, n) for t,n in nodein]
    nodeout = [(gtype if t == '$' else {t}, n) for t,n in nodeout]
  else:
    gtype = None
  if any(intersecttypes2(it, t) == set() for it,(t,n) in zip(intypes, nodein)) or any(intersecttypes2(ot, t) == set() for ot,(t,n) in zip(outtypes, nodeout)):
    return None
  return [nodedata, gtype]

def typename(t):
  return {
    'bool': 'bool',
    'float': 'float',
    'int': 'int',
    'string': 'string',
    'int3': 'int3',
    'Slot': '[FrooxEngine]FrooxEngine.Slot',
    'BodyNode': '[FrooxEngine]FrooxEngine.BodyNode',
    'Tool': '[FrooxEngine]FrooxEngine.ITool', # i don't think this was a good idea
  }[t]

def asmember(val):
  return {
    'ID': '###id###',
    'Data': val,
  }

def asid(val):
  return {
    'id': val,
    'Data': None,
  }

def fromcomponents(name, cs):
  return {'Name': name, 'Components': cs}

def generatenode(node, intypes, outtypes):
  nodedata = pfnodes.getnode(node[0][1])
  nodedata,generictype = choosenode(nodedata, intypes, outtypes)
  nodecomponent = {}
  #print(node[0][1], intypes, outtypes, nodeclass)
  nodeclass = nodedata['node']
  if generictype is not None:
    generictype = [*generictype][0]
    if type(nodeclass) == dict:
      if generictype in valuetypes:
        nodeclass = nodeclass['$value'] + '<' + typename(generictype) + '>'
      elif generictype in objecttypes:
        nodeclass = nodeclass['$object'] + '<' + typename(generictype) + '>'
      else:
        assert False, f'error: type {generictype} not recognized as object or value type'
    else:
      nodeclass = nodeclass + '<' + typename(generictype) + '>'
  
  print(nodeclass)
  print([n for t,n in nodedata['in']])
  nodecomponent = {
    'type': nodeclass,
  }
  if 'impulsein' in nodedata:
    print([n for n,c in nodedata['impulseout']])
  for (t,n),v in zip(nodedata['in'], node[3]):
    nodecomponent[n] = asmember('###' + repr(tuple(v)) + '###')
  if type(nodedata['out']) == list:
    print([n for t,n in nodedata['out']])
    for (t,n),v in zip(nodedata['out'], node[5]):
      nodecomponent[n] = asid(repr(tuple(v)))
  else:
    nodecomponent['id'] = repr(tuple(node[5][0]))
  return fromcomponents(re.sub('(^|<)[^<>,]*\\.', '\\1', nodeclass), [nodecomponent])

def generate(s):
  code = pft.parse(s)

  funcdefs = stripfunctions(code)

  functions = {}

  for funcname,funcargs,funccode in funcdefs:
    assert funcname not in functions, f'duplicate function definition: {funcname}'
    functions[funcname] = [funcargs, funccode]

  functions[()] = [[], code]

  for fdef in functions.values():
    args,code = fdef
    ivars,vvars = pfc.findvars(code)
    argvars = [['var', i - len(args)] for i in range(len(args))]
    vvars[(-1,)] = argvars
    pfc.resolvevars(code, ivars, vvars)
    datanodes = stripdatanodes(code)
    ivarlist = [v for vs in ivars.values() for n,v in vs]
    vvarlist = [v for vs in vvars.values() for n,v in vs]
    code = flattenbranches(code, ivarlist)
    if code[-1][0] == ['name', ('Return',)]:
      var = ['var', 'ie'] # this will be stripped by removejoins(), but it'll leave an impulse input on the first statement for an entry point
      ivarlist.append(var)
      code.insert(0, [['name', ('Continue',)], None, [var], [], [], []])
      ret = code[-1]
    else:
      ret = None
    addlinearimpulses(code, ivarlist)
    code += datanodes # code is now a list of nodes with no nesting
    code = removejoins(code)
    fdef.pop(0) # remove the arguments (they're in the variable list now)
    fdef[0] = code
    fdef.append(ivarlist)
    fdef.append(vvarlist)
    fdef.append(argvars)
    fdef.append(ret)

  # functions is now a dict of name to [func code, variables]

  # now inline them into each other

  funcdeps = {}

  for name,(code,ivarlist,vvarlist,args,ret) in functions.items():
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
  for name,(code,ivarlist,vvarlist,args,ret) in functions.items():
    # renumber the variables
    # to avoid collision
    for ivar in ivarlist:
      ivar[1] = next(vids)
    for vvar in vvarlist:
      vvar[1] = next(vids)
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

  finalcode = sum([[stmt for stmt in code if stmt[0][0] != 'fname'] for code,ivarlist,vvarlist,args,ret in functions.values()], [])
  ivarlist = sum([ivarlist for code,ivarlist,vvarlist,args,ret in functions.values()], [])
  vvarlist = sum([vvarlist for code,ivarlist,vvarlist,args,ret in functions.values()], [])

  for name,fcalls in calls.items():
    ret = functions[name][4]
    assert ret is not None, 'function must have return'
    argi = functions[name][0][0][2][0]
    reti = ret[2][0]
    args = functions[name][3]
    rets = ret[3]
    argis,retis,argvs,retvs = zip(*fcalls, strict = True)
    argvs = [*zip(*argvs, strict = True)]
    retvs = [*zip(*retvs, strict = True)]
    var = ['var', ('if', next(vids))]
    vvarlist.append(var)
    finalcode.append([['name', ('Impulse', 'Demultiplexer',)], None, [*argis], [], [argi], [var]])
    finalcode.append([['name', ('Impulse', 'Multiplexer',)], None, [reti], [var], [*retis], []])
    for arg,argv in zip(args, argvs):
      finalcode.append([['name', ('Multiplex',)], None, [], [var, *argv], [], [arg]])
    for ret,retv in zip(rets, retvs):
      for rv in retv:
        renamevar(finalcode, rv, ret)

  finalcode = [s for s in finalcode if s[0] not in [['name', ('Return',)]]]

  ivars = []
  vvars = []

  for ivar in ivarlist:
    argcount = 0
    retcount = 0
    for stmt in finalcode:
      name,tag,argsi,argsv,retsi,retsv = stmt
      if ivar in argsi:
        argcount += 1
      if ivar in retsi:
        retcount += 1
    if argcount == 0:
      continue
    assert argcount == 1, 'an impulse can only be used once'
    ivars.append(ivar)

  for vvar in vvarlist:
    argcount = 0
    retcount = 0
    for stmt in finalcode:
      name,tag,argsi,argsv,retsi,retsv = stmt
      if vvar in argsv:
        argcount += 1
      if vvar in retsv:
        retcount += 1
    if retcount == 0:
      assert argcount == 0, 'an undefined variable cannot be used'
      continue
    assert retcount == 1, 'a variable can only be defined once'
    vvars.append(vvar)

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
      for x,_ in ivaruses[tuple(ivar)]:
        deps[ivarlocs[tuple(ivar)]].add(x)

    for vvar in vvars:
      for x,_ in vvaruses[tuple(vvar)]:
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
          return '[' + ', '.join(render(['literal', t[2], x]) for x in t[3]) + ']'
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

  types = {tuple(var):'$' for var in vvars}

  def typeof(v):
    if v[0] == 'literal':
      if v[1] == 'rname':
        return '$' # nope not going to do this
      if v[1] in ['string', 'int', 'float', 'bool', 'null', 'BodyNode', 'int3', 'Slot', 'Tool']:
        return {v[1]}
    return types[tuple(v)]

  for node in finalcode:
    #print('n', node)
    intypes,outtypes = gettypes(pfnodes.getnode(node[0][1]), [typeof(v) for v in node[3]], [typeof(v) for v in node[5]])
    #print('t', intypes,outtypes)
    if set(['nope']) in intypes + outtypes or set() in intypes + outtypes:
      print('WARNING:', node[0], 'does not match', [typeof(v) for v in node[3]], [typeof(v) for v in node[5]])
    for it,iv in zip(intypes, node[3]):
      if iv[0] == 'var':
        #print('set', types[tuple(iv)], it, iv, intersecttypes(types[tuple(iv)], it))
        if set(['nope']) == intersecttypes(types[tuple(iv)], it) or set() == intersecttypes(types[tuple(iv)], it):
          print('WARNING:', node[0], 'does not match', [typeof(v) for v in node[3]], [typeof(v) for v in node[5]])
        types[tuple(iv)] = intersecttypes(types[tuple(iv)], it)
      if iv[0] == 'literal' and iv[1] == 'null':
        if len(it) > 1:
          print(f'WARNING: null with multiple possible types: {node}, {it}')
        iv[1] = [*it][0]
      if iv[0] == 'literal' and iv[1] == 'rname':
        if len(it) > 1:
          print(f'WARNING: reference with multiple possible types: {node}, {it}')
        iv[1] = [*it][0]
    for ot,ov in zip(outtypes, node[5]):
      #print('set', types[tuple(ov)], ot, ov, intersecttypes(types[tuple(ov)], ot))
      if set(['nope']) == intersecttypes(types[tuple(ov)], ot) or set() == intersecttypes(types[tuple(ov)], ot):
        print('WARNING:', node[0], 'does not match', [typeof(v) for v in node[3]], [typeof(v) for v in node[5]])
      types[tuple(ov)] = intersecttypes(types[tuple(ov)], ot)

  constants = set()

  for node in finalcode:
    for arg in node[3]:
      if arg[0] == 'var':
        continue
      constants.add(tuple(arg))
      print(arg)

  # the final node data
  nodes = []

  for c in constants:
    _,ctype,cval = c
    print(ctype, cval)
    if ctype == 'Slot':
      assert len(cval) == 1, 'reference names must not include whitespace'
      nodes.append(fromcomponents(ctype + ' input', [
        {
          'type': '[ProtoFluxBindings]FrooxEngine.FrooxEngine.ProtoFlux.CoreNodes.SlotSource',
          'id': repr(c),
          'Source': asmember('###' + repr((ctype, cval, 'source')) + '###'),
        },
        {
          'type': '[FrooxEngine]FrooxEngine.ProtoFlux.GlobalReference<' + typename(ctype) + '>',
          'id': repr((ctype, cval, 'source')),
          'Reference': asmember('###' + cval[0] + '###'),
        },
      ]))
    elif ctype in elementtypes:
      assert len(cval) == 1, 'reference names must not include whitespace'
      nodes.append(fromcomponents(ctype + ' input', [
        {
          'type': '[ProtoFluxBindings]FrooxEngine.FrooxEngine.ProtoFlux.CoreNodes.ElementSource<' + typename(ctype) + '>',
          'id': repr(c),
          'Source': asmember('###' + repr((ctype, cval, 'source')) + '###'),
        },
        {
          'type': '[FrooxEngine]FrooxEngine.ProtoFlux.GlobalReference<' + typename(ctype) + '>',
          'id': repr((ctype, cval, 'source')),
          'Reference': asmember('###' + cval[0] + '###'),
        },
      ]))
    elif ctype in valuetypes:
      nodes.append(fromcomponents(ctype + ' input', [{
        'type': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.ValueInput<' + typename(ctype) + '>',
        'id': repr(c),
        'Value': asmember(cval),
      }]))
    elif ctype in objecttypes:
      nodes.append(fromcomponents(ctype + ' input', [{
        'type': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.ValueObjectInput<' + typename(ctype) + '>',
        'id': repr(c),
        'Value': asmember(cval),
      }]))
    else:
      assert False, f'error: type {ctype} not recognized as object, value, or reference type'

  for node in finalcode:
    intypes = [typeof(v) for v in node[3]]
    outtypes = [typeof(v) for v in node[5]]
    nodes.append(generatenode(node, intypes, outtypes))
  
  for i,node in enumerate(nodes):
    node['Position'] = [0.5 + (i // 10) * 0.2, (i % 10) * 0.2, 0]
    print(node['Name'])
  
  return nodes

#with open('l.pft') as f:
#  s = f.read()

#print(generate(s))