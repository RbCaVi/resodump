# compiler
# identify and extract functions
#   currently function syntax is
#   a,b,c = Function(x, y, z) f: {
#     code
#   }
#   i'll probably change this later
#   anyway these are unscoped and usable anywhere
# resolve variables
#   value variables are single source multiple use
#   impulse variables are multiple source single use
#   variables are scoped inside their function (including the implicit main function)
# infer all types
#   may require access to the types of references
#   including functions - add virtual relay nodes between function calls and their functions
# flatten nesting
#   add missing subblocks (or error/warn?)
#   add explicit impulse outputs
#   add a node at the beginning of each subblock corresponding to the impulse output
#   some branches will connect to the statement after
#   add another impulse and connect it to a new node at the end of these
#   and to a new node after all of this with that impulse as an input
#   and put the subblocks between
# add implicit linear impulses
#   only taking into account nodes that have impulse inputs and outputs
#   when one node has one (implicit) impulse out and the next has one (implicit) impulse in
#   accept when the next node has no impulse inputs
#   or when there is no next node
#   special case for Call Display - does not break the chain
#   error or warn on node with implicit impulse input without an implicit impulse output before it
# arrange nodes
#   separate per function
#   not sure how though
#   some kind of spring layout?
#   inputs and outputs clamped to the boundaries
#   nodes push apart from each other vertically when they are close together horizontally
#   connected nodes pull together horizontally (and vertically)
#   the spring force will probably be like -k * x / (x + d)
#   (weak pull + strong push)
#   and i guess it's calculated separately for x and y
# finally generate the nodes
#   (into the json format from frdtgen.py)
#   all of it goes under one slot
#     then the functions go under their own slots inside that
#     a function call is replaced with a group of relays
#     and the multiplexers between them are on a back layer under the top slot

# i'm trying to make better diagnostics this time
# like showing where a type error came from instead of just saying there's a type error

class CompileContext:
  def __init__(self):
    self.messages = []
    self.tempmessages = []
  
  def addmessage(self, message):
    self.messages.append(message)
  
  def addtempmessage(self, message):
    self.tempmessages.append(message)

class CompileStmt:
  @staticmethod
  def fromstmt(stmt, context):
    self = CompileStmt()
    self.source = stmt
    self.iin = stmt.func.iin
    self.vin = stmt.func.vin
    self.iout = stmt.assign.iout
    self.vout = stmt.assign.vout
    self.funcname = stmt.func.name.name
    self.funcisbuiltin = stmt.func.name.builtin
    context.addmessage(['statement', self.funcname, self.funcisbuiltin, stmt.func.name])
    self.generic = stmt.func.tag
    self.subblocks = {}
    self.subblockdatas = {}
    for subblock in stmt.subblocks:
      if subblock.label in self.subblocks:
        context.addmessage(['duplicate subblock label', subblock, self.subblocks[subblock.label]])
      else:
        self.subblocks[subblock.label] = [CompileStmt.fromstmt(s, context) for s in subblock.stmts]
        self.subblockdatas[subblock.label] = subblock
    return self

def visitstmts(path, stmts, beforestmts, afterstmts, beforestmt, afterstmt):
  # path is a tuple
  beforestmts(path, stmts)
  for i,stmt in enumerate(stmts):
    visitstmt(path + (i,), stmt, beforestmts, afterstmts, beforestmt, afterstmt)
  afterstmts(path, stmts)

def visitstmt(path, stmt, beforestmts, afterstmts, beforestmt, afterstmt):
  beforestmt(path, stmt)
  for name,stmts in stmt.subblocks.items():
    visitstmts(path + (name,), stmts, beforestmts, afterstmts, beforestmt, afterstmt)
  afterstmt(path, stmt)

def nothing(path, s):
  pass

class CompileFunc:
  @staticmethod
  def new(argnames, retnames, stmts):
    self = CompileFunc()
    self.argnames = argnames
    self.retnames = retnames
    self.stmts = stmts
    return self

def extractfunctions(stmts, context):
  funcs = {}
  def afterstmts(path, stmts):
    print([(stmt.funcname, stmt.funcisbuiltin) for stmt in stmts])
    newfuncs = [stmt for stmt in stmts if (stmt.funcname, stmt.funcisbuiltin) == (('Function',), True)]
    for newfunc in newfuncs:
      if len(newfunc.iin) > 0:
        context.addmessage(['function with impulse inputs', newfunc.iin])
      if len(newfunc.iout) > 0:
        context.addmessage(['function with impulse outputs', newfunc.iout])
      if newfunc.generic is not None:
        context.addmessage(['function with generic', newfunc.generic])
      if any(v.kind != pft2.IDENT for v in newfunc.vin):
        context.addmessage(['function with non identifier arguments', [v for v in newfunc.vin if v.kind != pft2.IDENT]])
      argnames = [v.value for v in newfunc.vin if v.kind == pft2.IDENT]
      retnames = [v.name for v in newfunc.vout]
      if len(newfunc.subblocks) > 1:
        context.addmessage(['function with multiple subblocks', newfunc])
      funcname,fstmts = next(iter(newfunc.subblocks.items()))
      if funcname in funcs:
        context.addmessage(['duplicate function name', newfunc.subblocksdata[funcname], funcs[funcname]])
      else:
        funcs[funcname] = CompileFunc.new(argnames, retnames, fstmts)
        context.addmessage(['function', funcname, funcs[funcname]])
    stmts[:] = [stmt for stmt in stmts if (stmt.funcname, stmt.funcisbuiltin) != (('Function',), True)]
  visitstmts((), stmts, nothing, afterstmts, nothing, nothing)
  funcs['<MAIN>'] = CompileFunc.new([], [], stmts)
  return funcs

if __name__ == '__main__':
  import pft2
  
  with open('l.pft') as f:
    s = f.read()
  stmts = pft2.parse(s)
  context = CompileContext()
  stmts = [CompileStmt.fromstmt(s, context) for s in stmts]
  funcs = extractfunctions(stmts, context)
  
  for message in context.messages:
    print(message)
  
  print()
  
  for tempmessage in context.tempmessages:
    print(tempmessage)