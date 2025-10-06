# protoflux nodes <3

import pickle
import collections
import traceback

ts = collections.defaultdict(set)

class PfType:
  def __init__(self, dataclass, name):
    self.dataclass = dataclass
    self.name = name
    ts[self.name].add(self.dataclass)
  
  def __str__(self):
    did = {
      'Ref': '&',
      'Value': '#',
      'Object': '$',
    }[self.dataclass]
    return f'{did}{self.name}'

class PfInputInfo:
  def __init__(self, name, typ):
    self.name = name
    self.typ = typ
  
  def __str__(self):
    return f'{self.name}: {self.typ}'

class PfOutputInfo:
  def __init__(self, name, typ):
    self.name = name
    self.typ = typ
  
  def __str__(self):
    if self.name is None:
      return f'{self.typ}'
    return f'{self.name}: {self.typ}'

class PfInputListInfo:
  def __init__(self, name, typ):
    self.name = name
    self.typ = typ
  
  def __str__(self):
    return f'{self.name}: {self.typ}'

class PfOutputListInfo:
  def __init__(self, name, typ):
    self.name = name
    self.typ = typ
  
  def __str__(self):
    return f'{self.name}: {self.typ}'

def getrefinfo(r):
  return PfInputInfo(r.Name, PfType('Ref', r.ValueType))

def getinputinfo(i):
  return PfInputInfo(i.Name, PfType(i.DataClass, i.InputType))

def getoutputinfo(o):
  if o.IsImplicit:
    return PfOutputInfo(None, PfType(o.DataClass, o.OutputType))
  return PfOutputInfo(o.Name, PfType(o.DataClass, o.OutputType))

def getinputlistinfo(il):
  return PfInputListInfo(il.Name, PfType(il.DataClassConstraint, il.TypeConstraint))

def getoutputlistinfo(ol):
  return PfOutputListInfo(ol.Name, PfType(ol.DataClassConstraint, ol.TypeConstraint))

class Node:
  hasvarargs = False
  
  def strargs_(self):
    return ', '.join(map(str, self.inputinfos))
  
  def strvarargs_(self):
    return f'*{str(self.inputsinfo)}'
  
  def strargs(self):
    if self.hasvarargs:
      return self.strvarargs_()
    return self.strargs_()
  
  def strrets_(self):
    return ', '.join(map(str, self.outputinfos))
  
  def strrets(self):
    return self.strrets_()
  
  def strsig(self):
    return f'''{self.strargs()} -> {self.strrets()}'''

class ConcreteNode(Node):
  def __init__(self, typename, generics, metadata):
    self.typename = typename
  
  def __str__(self):
    return f'''{type(self).__name__} {self.typename}:\n\t{self.strsig()}'''
  
  def specialize(self, intypes, outtypes, generics, context):
    return specializeconcrete(self.inputinfos, self.outputinfos, intypes, outtypes, generics, context, None)

class GenericNode(Node): # specifically one parameter generic
  def __init__(self, typename, generics, metadata):
    self.typename = typename.split('`')[0]
    typeparam = generics[0]
    self.typeparamname = typeparam[0]
    dataclass = 'Value' if 'System.ValueType' in typeparam[1] else 'Object'
    self.typeparamconstraints = [PfType(dataclass, '__any__')] + [PfType(dataclass, t) for t in typeparam[1] if t != 'System.ValueType']
  
  def __str__(self):
    return f'''{type(self).__name__} {self.typename}<{' '.join([self.typeparamname] + [str(c) for c in self.typeparamconstraints])}>:\n\t{self.strsig()}'''
  
  def specialize(self, intypes, outtypes, generics, context):
    # how do i choose a generic type?
    return specializegeneric(self.typeparamname, self.typeparamconstraints, self.inputinfos, self.outputinfos, intypes, outtypes, generics, context, None)

def specializeconcrete(nodeinputs, nodeoutputs, inputtypes, outputtypes, generics, context, extradata):
  if len(inputtypes) != len(nodeinputs):
    context.addtempmessage(['wrong input count'])
    return None
  if len(outputtypes) != len(nodeoutputs) and len(outputtypes) != 0:
    context.addtempmessage(['wrong output count'])
    return None
  for i,(it,ni) in enumerate(zip(inputtypes, nodeinputs)):
    if not it.contains(ni.typ):
      context.addtempmessage(['unmatched input type', i])
      return None
  for i,(ot,no) in enumerate(zip(outputtypes, nodeoutputs)):
    if not ot.contains(no.typ):
      context.addtempmessage(['unmatched output type', i])
      return None
  return (
    extradata,
    [it.under(ni.typ) for it,ni in zip(inputtypes, nodeinputs)],
    [ot.over(no.typ) for ot,no in zip(outputtypes, nodeoutputs)],
  )

def specializegeneric(generictypename, generictypeconstraints, nodeinputs, nodeoutputs, inputtypes, outputtypes, generics, context, extradata):
  if len(inputtypes) != len(nodeinputs):
    context.addtempmessage(['wrong input count'])
    return None
  if len(outputtypes) != len(nodeoutputs) and len(outputtypes) != 0:
    context.addtempmessage(['wrong output count'])
    return None
  if generics is None: # no generic arguments
    generic = PfTypeRange(generictypeconstraints, []) # it's always a subtype of the type constraints
    for i,(it,ni) in enumerate(zip(inputtypes, nodeinputs)):
      if ni.typ.name == generictypename:
        generic = generic.over(it)
      elif not it.contains(ni.typ):
        context.addtempmessage(['unmatched input type', i])
        return None
    for i,(ot,no) in enumerate(zip(outputtypes, nodeoutputs)):
      if no.typ.name == generictypename:
        generic = generic.under(ot)
      elif not ot.contains(no.typ):
        context.addtempmessage(['unmatched output type', i])
        return None
  else: # one generic argument
    typ = PfType(getdataclass(generics[0]), generics[0])
    generic = PfTypeRange(generictypeconstraints + [typ], [typ]) # it's always a subtype of the type constraints
    for i,(it,ni) in enumerate(zip(inputtypes, nodeinputs)):
      if ni.typ.name == generictypename:
        if not it.contains(typ):
          context.addtempmessage(['unmatched generic input type', i])
          return None
      elif not it.contains(ni.typ):
        context.addtempmessage(['unmatched input type', i])
        return None
    for i,(ot,no) in enumerate(zip(outputtypes, nodeoutputs)):
      if no.typ.name == generictypename:
        if not ot.contains(typ):
          context.addtempmessage(['unmatched generic output type', i])
          return None
      elif not ot.contains(no.typ):
        context.addtempmessage(['unmatched output type', i])
        return None
  return (
    (generic, extradata),
    [it.under(ni.typ if ni.typ.name != generictypename else generic) for it,ni in zip(inputtypes, nodeinputs)],
    [ot.over(no.typ if no.typ.name != generictypename else generic) for ot,no in zip(outputtypes, nodeoutputs)],
  )

class ConcreteDataNode(ConcreteNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]

class ConcreteVariadicNode(ConcreteNode):
  hasvarargs = True
  
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputsinfo = getinputlistinfo(metadata.DynamicInputs[0])
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
  
  def specialize(self, intypes, outtypes, generics, context):
    variadiccount = len(intypes)
    inputinfos = [self.inputsinfo for _ in range(variadiccount)]
    return specializeconcrete(inputinfos, self.outputinfos, intypes, outtypes, generics, context, variadiccount)

class ConcreteFVariadicNode(ConcreteNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.inputsinfo = getinputlistinfo(metadata.DynamicInputs[0])
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
  
  def strargs(self):
    return f'{self.strargs_()}, {self.strvarargs_()}'
  
  def specialize(self, intypes, outtypes, generics, context):
    variadiccount = len(intypes) - len(self.inputinfos)
    if variadiccount < 0:
      context.addtempmessage(['not enough arguments'])
      return None
    inputinfos = self.inputinfos + [self.inputsinfo for _ in range(variadiccount)]
    return specializeconcrete(inputinfos, self.outputinfos, intypes, outtypes, generics, context, variadiccount)

class ConcreteLinearNode(ConcreteNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
    assert metadata.FixedOperations[0].IsSelf
    self.nextname = metadata.FixedImpulses[0].Name
  
  def strargs(self):
    return f'{self.strargs_()} @'
  
  def strrets(self):
    return f'{self.strrets_()} @ {self.nextname}'

class ConcreteFlowNode(ConcreteNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
    assert metadata.FixedOperations[0].IsSelf
    self.impulses = [i.Name for i in metadata.FixedImpulses]
  
  def strargs(self):
    return f'{self.strargs_()} @'
  
  def strrets(self):
    return f'''{self.strrets_()} @ {', '.join(self.impulses)}'''

class ConcreteUnrefEventNode(ConcreteNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
    self.event = metadata.FixedImpulses[0].Name
  
  def strrets(self):
    return f'{self.strrets_()} @ {self.event}'

class ConcreteRefEventNode(ConcreteNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.refinfo = getrefinfo(metadata.FixedGlobalRefs[0])
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
    self.events = [i.Name for i in metadata.FixedImpulses]
  
  def strargs(self):
    return f'[{str(self.refinfo)}], {self.strargs_()}'
  
  def strrets(self):
    return f'''{self.strrets_()} @ {', '.join(self.events)}'''

class GenericDataNode(GenericNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]

class GenericVariadicNode(GenericNode):
  hasvarargs = True
  
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputsinfo = getinputlistinfo(metadata.DynamicInputs[0])
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
  
  def specialize(self, intypes, outtypes, generics, context):
    variadiccount = len(intypes)
    inputinfos = [self.inputsinfo for _ in range(variadiccount)]
    return specializegeneric(self.typeparamname, self.typeparamconstraints, inputinfos, self.outputinfos, intypes, outtypes, generics, context, variadiccount)

class GenericFVariadicNode(GenericNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.inputsinfo = getinputlistinfo(metadata.DynamicInputs[0])
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
  
  def strargs(self):
    return f'{self.strargs_()}, {self.strvarargs_()}'
  
  def specialize(self, intypes, outtypes, generics, context):
    variadiccount = len(intypes) - len(self.inputinfos)
    if variadiccount < 0:
      context.addtempmessage(['not enough arguments'])
      return None
    inputinfos = self.inputinfos + [self.inputsinfo for _ in range(variadiccount)]
    return specializegeneric(self.typeparamname, self.typeparamconstraints, inputinfos, self.outputinfos, intypes, outtypes, generics, context, variadiccount)

class GenericLinearNode(GenericNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
    assert metadata.FixedOperations[0].IsSelf
    assert metadata.FixedImpulses[0].Name == 'Next'
  
  def strargs(self):
    return f'{self.strargs_()} @'
  
  def strrets(self):
    return f'{self.strrets_()} @ Next'

class GenericFlowNode(GenericNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
    assert metadata.FixedOperations[0].IsSelf
    self.impulses = [i.Name for i in metadata.FixedImpulses]
  
  def strargs(self):
    return f'{self.strargs_()} @'
  
  def strrets(self):
    return f'''{self.strrets_()} @ {', '.join(self.impulses)}'''

class GenericUnrefEventNode(GenericNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
    self.event = metadata.FixedImpulses[0].Name
  
  def strrets(self):
    return f'{self.strrets_()} @ {self.event}'

class GenericRefEventNode(GenericNode):
  def __init__(self, typename, generics, metadata):
    super().__init__(typename, generics, metadata)
    self.refinfo = getrefinfo(metadata.FixedGlobalRefs[0])
    self.inputinfos = [getinputinfo(i) for i in metadata.FixedInputs]
    self.outputinfos = [getoutputinfo(o) for o in metadata.FixedOutputs]
    self.events = [i.Name for i in metadata.FixedImpulses]
  
  def strargs(self):
    return f'[{str(self.refinfo)}], {self.strargs_()}'
  
  def strrets(self):
    return f'''{self.strrets_()} @ {', '.join(self.events)}'''

groupclasses = {
  'datac': ConcreteDataNode,
  'datag': GenericDataNode,
  'variadicg': GenericVariadicNode,
  'variadicc': ConcreteVariadicNode,
  'fvariadicg': GenericFVariadicNode,
  'fvariadicc': ConcreteFVariadicNode,
  'actiong': GenericLinearNode,
  'actionc': ConcreteLinearNode,
  'flowg': GenericFlowNode,
  'flowc': ConcreteFlowNode,
  'globaleventsg': GenericUnrefEventNode,
  'globaleventsc': ConcreteUnrefEventNode,
  'eventsg': GenericRefEventNode,
  'eventsc': ConcreteRefEventNode,
}

with open('protoflux-node-data.pkl', 'rb') as f:
  nodelist = pickle.load(f)
  nodes = {}
  for name,*node in nodelist:
    if name not in nodes:
      nodes[name] = []
    if node[0] in groupclasses:
      node = groupclasses[node[0]](*node[1:])
    nodes[name].append(node)

#for node in nodes['Add']:
#  print(*node)

for node in sum(nodes.values(), []):
  if isinstance(node, list):
    #print(*node)
    pass
  else:
    print(node)
    pass

print({node[0] for node in sum(nodes.values(), []) if isinstance(node, list)})
print(len([node for node in sum(nodes.values(), []) if isinstance(node, list)]))
[print(x) for x in sorted({(node[3].signature(), name) for name,ns in nodes.items() for node in ns if isinstance(node, list)})]
print({k:v for k,v in ts.items() if len(v) > 1 and v != {'Object', 'Ref'}})

# uhh node selection algorithm

# given a node and list of input and output type ranges (and idk a few other things)
# return whether this node can be specialized to match the inputs and outputs
# and the parameters of that specialization if it exists
# or actually None | (parameters, specialized type ranges)
# tbh

# a type range has lists of top and bottom types

# the top is the larger types (supertypes)
# bottom is smaller types

# a type is a pair of data class (value or object) and type name

def getdataclass(t):
  return t[0]

def gettypename(t):
  return t[1]

def issubtype(t1, t2):
  # t1 of t2
  # a <= kind of relationship
  # if t1 implicitly casts to t2
  if t1 == t2:
    return True
  if getdataclass(t1) != getdataclass(t2):
    return False
  if t2.name == '__any__':
    return True
  # uhhh
  # values and objects
  if getdataclass(t1) == 'Value':
    # values are:
    #  - enums
    #  - structs
    #  - boolean
    #  - numeric types (integer, floating point)
    #  - vectors of numeric (2, 3, 4)
    #  - matrices of numeric (2x2, 3x3, 4x4)
    #  - floating point quaternions
    #  - color and colorX
    # of these, enums and structs are their own types
    # boolean doesn't cast implicitly
    # numeric types follow the rule:
    #   byte -> short -> int -> long
    #   half -> float -> double
    #   byte -> half
    #   short -> float
    #   int -> double
    #   signed and unsigned integers don't cast together
    #   an unsigned integer will cast to the next type up signed int
    # maybe float4 and floatQ and color can cast?
    floatingpoint = ['System.Half', 'System.Single', 'System.Double']
    signedint = ['System.SByte', 'System.Int16', 'System.Int32', 'System.Int64']
    unsignedint = ['System.Byte', 'System.UInt16', 'System.UInt32', 'System.UInt64']
    numeric = floatingpoint + signedint + unsignedint
    if gettypename(t1) in numeric and gettypename(t2) in numeric:
      if gettypename(t1) in floatingpoint and gettypename(t2) in floatingpoint:
        return floatingpoint.index(gettypename(t1)) <= floatingpoint.index(gettypename(t2))
      if gettypename(t1) in signedint and gettypename(t2) in signedint:
        return signedint.index(gettypename(t1)) <= signedint.index(gettypename(t2))
      if gettypename(t1) in unsignedint and gettypename(t2) in unsignedint:
        return unsignedint.index(gettypename(t1)) <= unsignedint.index(gettypename(t2))
      if gettypename(t1) in signedint and gettypename(t2) in unsignedint:
        return False # signed -/> unsigned
      if gettypename(t1) in unsignedint and gettypename(t2) in signedint:
        return unsignedint.index(gettypename(t1)) < signedint.index(gettypename(t2))
      if gettypename(t1) in floatingpoint and gettypename(t2) in signedint + unsignedint:
        return False # float -/> int
      if gettypename(t1) in signedint and gettypename(t2) in floatingpoint:
        return signedint.index(gettypename(t1)) < floatingpoint.index(gettypename(t2))
      if gettypename(t1) in unsignedint and gettypename(t2) in floatingpoint:
        return unsignedint.index(gettypename(t1)) < floatingpoint.index(gettypename(t2))
    if gettypename(t1) in numeric and gettypename(t2) not in numeric:
      return False
    if gettypename(t1) not in numeric and gettypename(t2) in numeric:
      return False
    # need vectors and matrices too i guess
    return False
  else:
    # and objects... idk
    # maybe dump the type hierarchy as well somehow?
    # instantiate a python.net instance to check subtyping frfr
    # idk just explicitly cast it
    return False

class PfTypeRange:
  def __init__(self, top, bottom):
    self.top = top
    self.bottom = bottom
  
  def contains(self, other):
    # other is a PfType
    return all(issubtype(other, t) for t in self.top) and all(issubtype(t, other) for t in self.bottom)
  
  def under(self, other):
    if isinstance(other, PfTypeRange):
      others = other.top
    else:
      others = [other]
    return PfTypeRange(self.top + others, self.bottom)
  
  def over(self, other):
    if isinstance(other, PfTypeRange):
      others = other.bottom
    else:
      others = [other]
    return PfTypeRange(self.top, self.bottom + others)
  
  def __repr__(self):
    return f'''({' '.join(str(t) for t in self.bottom)} | {' '.join(str(t) for t in self.top)})'''

def choosenode(node, intypes, outtypes):
  group,typename,generics,metadata = node
  if group == 'datac':
    # simplest group
    # just check the types
    if all(it.contains((ni.DataClass, ni.InputType)) for it,ni in zip(intypes, node.FixedInputs, strict = True)) and all(ot.contains((no.DataClass, no.OutputType)) for ot,no in zip(intypes, node.FixedOutputs, strict = True)):
      return ((), [it.under((ni.DataClass, ni.InputType)) for it,ni in zip(intypes, node.FixedInputs, strict = True)], [ot.over((no.DataClass, no.OutputType)) for ot,no in zip(intypes, node.FixedOutputs, strict = True)])
  if group == 'variadicc':
    # check the one input type
    dyninput = node.DynamicInputs[0]
    intype = (dyninput.DataClassConstraint, dyninput.TypeConstraint)
    if all(it.contains(intype) for it in intypes) and all(ot.contains((no.DataClass, no.OutputType)) for ot,no in zip(intypes, node.FixedOutputs, strict = True)):
      return ((), [it.under(intype) for it in intypes], [ot.over((no.DataClass, no.OutputType)) for ot,no in zip(intypes, node.FixedOutputs, strict = True)])
  else:
    print(node)