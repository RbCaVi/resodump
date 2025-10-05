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