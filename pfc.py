# pft compiler
# or at least intermediate representation

import itertools

def walk(code, f, path = ()):
  for i1,s in enumerate(code):
    f(s, path + (i1,))
    for i2,subblock in enumerate(s[6]):
      walk(subblock[1], f, path + (i1, i2))

def findvars(code):
  ivars = {}
  vvars = {}
  vids = itertools.count()
  def f(stmt, path):
    if stmt[0] in [['name', ['If']], ['name', ['Impulse', 'Multiplexer']]]:
      # if and impulse multiplexer can return values :)
      #path = path[:-1] + (path[-1] + 0.5,) # nope
      pass
    ivars[path] = [(vn, ['var', next(vids)]) for vn in stmt[2]]
    vvars[path] = [(vn, ['var', next(vids)]) for vn in stmt[3]]
  walk(code, f)
  return ivars, vvars

def evenmatch(path1, path2):
  return len([*itertools.takewhile(lambda x: x[0] == x[1], zip(path1, path2))]) % 2 == 0

def inscope(path, checkpath):
  # whether checkpath is in scope at path
  # the condition is:
  #   matches an even number of indices (ending on a subblock index) at the start
  #   and the first non matching one is less
  # or
  #   is a substring
  return (path > checkpath and evenmatch(path, checkpath)) or checkpath == path[:len(checkpath)]

# map of constants to types
constanttypes = {
  'LeftHand': 'BodyNode',
}

def resolvevar(var, vars_, vpath):
  if var[0] != 'name':
    return var
  paths = sorted(filter(lambda p: inscope(vpath, p), vars_.keys()), reverse = True)
  for path in paths:
    for varname,varid in vars_[path]:
      if varname == var:
        return varid
  name = ' '.join(var[1])
  if name.lower() == 'true':
    return ['literal', 'bool', True]
  if name.lower() == 'false':
    return ['literal', 'bool', False]
  if name.lower() == 'null':
    return ['literal', 'null', None]
  if name in constanttypes:
    return ['literal', constanttypes[name], name]
  assert False, f'{var}, {vpath}, {paths}, {[vars_[path] for path in paths]}'

def resolvevars(code, ivars, vvars):
  # basically search backwards in the order they appear in the program
  # include statements before and their subblocks
  # and statements above (not their subblocks)
  # and statements before statements above and their subblocks
  # should be all statements before except in adjacent subblocks
  # this disallows cyclic impulse and data chains
  def f(stmt, path):
    stmt[2] = [resolvevar(v, ivars, path) for v in stmt[2]]
    stmt[3] = [resolvevar(v, vvars, path) for v in stmt[3]]
    stmt[4] = [vi for vn,vi in (ivars[path] if path in ivars else ivars[path[:-1] + (path[-1] + 0.5,)])]
    stmt[5] = [vi for vn,vi in (vvars[path] if path in vvars else vvars[path[:-1] + (path[-1] + 0.5,)])]
  walk(code, f)