# pft compiler
# or at least intermediate representation

def walk(code, f, path = ()):
  for s in code:
    if s[0] == 'stmt':
      f(s, path)
      for i,subblock in enumerate(s[5]):
        walk(subblock[2], path + (i,))
    else:
      assert False, f'non statement in code: {s}'

def findvars(code):
  vars_ = {}
  def f(stmt, path):
    if stmt[1] is not None:
      vars_[path] = stmt[1]
  walk(code, f)
  return vars_