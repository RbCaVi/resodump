# compiler structure <3
# pull out functions
# "inline" functions (either actual inline or the multiplexer trick (both only work with non recursive functions))
# infer types
# connect linear impulses
# add Join/Continue + flatten nested code (subblocks)

# i'm trying to make better diagnostics this time though
# like showing where a type error came from instead of just saying there's a type error

class CompileStmt:
  def __init__(self, stmt):
    # assign basic properties
    self.iin
    self.vin
    self.iout
    self.vout
    self.func # name, is builtin, tag (generic)
    self.subblocks
    # check each of the four connection sets that they are either empty or matching size with the definition
    # also the subblock names

if __name__ == '__main__':
  import pft2
  
  with open('l.pft') as f:
    s = f.read()
  stmts = pft2.parse(s)
  print(pft2.dumpstmts(stmts))