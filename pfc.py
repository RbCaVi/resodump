# pft compiler
# or at least intermediate representation

def walk(code, f, path = ()):
  for i1,s in enumerate(code):
    if s[0] == 'stmt':
      f(s, path + (i1,))
      for i2,subblock in enumerate(s[5]):
        walk(subblock[2], f, path + (i1, i2))
    else:
      assert False, f'non statement in code: {s}'

def findvars(code):
  vars_ = {}
  def f(stmt, path):
    if stmt[1] is not None:
      vars_[path] = stmt[1]
  walk(code, f)
  return vars_