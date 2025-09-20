# export protoflux nodes
# https://github.com/Banane9/ResoniteWikiHelpers/blob/master/ResoniteWikiHelpers.ProtofluxNodeExport/Program.cs
# rewritten in python
# because i don't want to install a c sharp compiler <3

# original license:
# MIT License
# 
# Copyright (c) [year] [fullname]
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
libpath = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Resonite'
sys.path.append(libpath)
import itertools


from pythonnet import load
load("coreclr")

import clr
from System.Reflection import Assembly
clr.AddReference('Elements.Core')
clr.AddReference('ProtoFlux.Core')
from Elements.Core import StringHelper
from ProtoFlux.Core import NodeMetadataHelper, NodeCategoryAttribute

print('loaded libraries')

assemblynames = ['FrooxEngine.dll', 'ProtoFlux.Core.dll', 'Protoflux.Nodes.Core.dll', 'Protoflux.Nodes.FrooxEngine.dll']
assemblies = [Assembly.LoadFrom(os.path.join(libpath, name)) for name in assemblynames]
INode = assemblies[1].GetType('ProtoFlux.Core.INode', True) # True - throw if not found

print('loaded assemblies')

#Assembly.LoadFrom(os.path.join(libpath, 'System.Numerics.Vectors.dll')) # FrooxEngine.dll requires this before .GetTypes()
types = itertools.chain.from_iterable(a.GetTypes() for a in assemblies)
types = [*filter(lambda t: not t.IsAbstract and t.IsPublic and INode.IsAssignableFrom(t), types)]

print('extracted types')

def getoptionalname(x):
  if x is not None:
    return x.Name

def nullconcat(a, b):
  if a is None or b is None:
    return None
  return a + b

def firstornone(l):
  if len(l) > 0:
    return l[0]

types = [t for t in types if not any([t.FullName.startswith(x) for x in [
  'FrooxEngine.ProtoFlux.CoreNodes.AsyncMethodProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.AsyncValueFunctionProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.AsyncObjectFunctionProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.SyncMethodProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.SyncValueFunctionProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.SyncObjectFunctionProxy',
  'ProtoFlux.Runtimes.Execution.NestedNode',
  'ProtoFlux.Runtimes.Execution.Nodes.Link',
]])]

typedatas = [(
  t,
  metadata := NodeMetadataHelper.GetMetadata(t),
  nullconcat('Root/', getoptionalname(firstornone(t.GetCustomAttributes(NodeCategoryAttribute, True)))) or 'Root',
  metadata.Name or StringHelper.BeautifyName(metadata.Overload or t.Name) # the metadata.Overload field is (right now) always overshadowed by metadata.Name
) for t in types]

#key1 = lambda x: x[1].Overload or x[3] # original code
#key2 = lambda x: x[3] # something else idk
#key = key1
#gs = [(k, [*v]) for k,v in itertools.groupby(sorted(typedatas, key = key), key)]

#metadatas = [x[1] for x in typedatas]

#{j for j in {x[3] for x in typedatas} if len({y[2] for y in typedatas if y[3] == j}) > 1} # trying to check for nodes with the same name under different paths

for typ,meta,path,name in typedatas:
  print(typ, name)
  # input impulses
  for x in meta.FixedOperations:
    print('  meta.FixedOperations', x)
  for x in meta.DynamicOperations:
    print('  meta.DynamicOperations', x)
  # input values
  for x in meta.FixedInputs:
    print('  meta.FixedInputs', x)
  for x in meta.DynamicInputs:
    print('  meta.DynamicInputs', x)
  # output impulses
  for x in meta.FixedImpulses:
    print('  meta.FixedImpulses', x)
  for x in meta.DynamicImpulses:
    print('  meta.DynamicImpulses', x)
  # output values
  for x in meta.FixedOutputs:
    print('  meta.FixedOutputs', x)
  for x in meta.DynamicOutputs:
    print('  meta.DynamicOutputs', x)

for name in sorted({name for _,_,_,name in typedatas}):
  print(name)
  
  for typ,meta,path,tname in typedatas:
    if tname == name:
      print(' ', path, typ)

def filtered(f, typedatas = typedatas):
  typedatas2 = [x for x in typedatas if f(x)]
  for name in sorted({name for _,_,_,name in typedatas2}):
    print(name)
    for typ,meta,path,tname in typedatas2:
      if tname == name:
        print(' ', path, typ)

# if .FixedInputCount == .FixedArgumentCount, then the node doesn't have any impulse inputs or outputs
# .FixedArgumentCount is ones that are not marked conditional
# not sure why this matters

# :? and ?? have some (but not all) inputs non conditional

# these have all inputs conditional
# but no impulses in or out
# not sure why
# maybe they're updated on every tick or something
#   Constant Lerp
#   Constant Slerp
#   Smooth Lerp
#   Smooth Slerp
#   Delay
#   Delta
#   Display
#   Eval Point
#   Get Active Locomotion Module
#   Nearest User Foot
#   Nearest User Hand
#   Nearest User Head
#   Object Field Drive`1
#   Reference Drive`1
#   Value Field Drive`1
#   Field As Variable`1
#   Ref As Variable
#   User Ref As Variable

# generics
generic = [x for x in typedatas if len(x[0].GetGenericArguments()) != 0]
generic1 = [x for x in generic if len(x[0].GetGenericArguments()) == 1]
generic2 = [x for x in generic if len(x[0].GetGenericArguments()) == 2 and x[0].GetGenericArguments()[0].Name != 'C'] # because there are generic versions of some nodes that take a context type as the first parameter # this is literally spherical harmonics evaluate and object cast
# 2 generic parameters is the max for non proxy nodes (proxy nodes go up to like 7)

concrete = [x for x in typedatas if len(x[0].GetGenericArguments()) == 0]

# non alphanumeric names get renamed <3
rename = {
  '0/1 (float)': 'Zero One Float',
  '0/1 (float2)': 'Zero One Float2',
  '0/1 (float3)': 'Zero One Float3',
  '0/1 (float4)': 'Zero One Float4',
  '0/1 (int)': 'Zero One Int',
  '0/1 (int2)': 'Zero One Int2',
  '0/1 (int3)': 'Zero One Int3',
  '0/1 (int4)': 'Zero One Int4',
  
  '+': 'Add',
  '-': 'Subtract', # StringHelper.BeautifyName() replaces '-' with ' ' :skull:
  '±': 'Add Subtract',
  '×': 'Multiply',
  '÷': 'Divide',
  '%': 'Modulo',
  '<<': 'Shift Left',
  '>>': 'Shift Right',
  
  # these require both a reference and a generic type
  '++': '-- Increment',
  '--': '-- Decrement',
  'Ref To Output': '-- Ref To Output',
  'Write': '-- Write',
  'Write Latch': '-- Write Latch',
  
  '1/(π/2)': 'Inverse Half Pi',
  '1/(π/4)': 'Inverse Quarter Pi',
  '1/d T': 'Inverse dT',
  '1/π': 'Inverse Pi',
  '1/τ': 'Inverse Tau',
  'Π/2': 'Half Pi',
  'Π/4': 'Quarter Pi',
  
  '==': 'Equal',
  '!=': 'Not Equal',
  '≈': 'Approximately Equal',
  '!≈': 'Approximately Not Equal',
  '<': 'Less Than',
  '>': 'Greater Than',
  '≤': 'Less Than Or Equal',
  '≥': 'Greater Than Or Equal',
  
  "' '<size=25%>( Space)": 'Space',
  'New Line ( OS)': 'OS Newline',
  '\\\\a<size=25%>( Bell)': 'Bell',
  '\\\\b<size=25%>( Backspace)': 'Backspace',
  '\\\\f<size=25%>( Form Feed)': 'Form Feed',
  '\\\\n<size=25%>( New Line)': 'Newline',
  '\\\\r<size=25%>( Carridge Return)': 'Carriage Return',
  '\\\\t<size=25%>( Tab)': 'Tab',
  '\\\\v<size=25%>( Vertical Tab)': 'Vertical Tab',
  
  'Sin<sup> 1': 'Asin',
  'Cos<sup> 1': 'Acos',
  'Tan<sup> 1': 'Atan',
  'E<sup>n': 'Exp',
  'Log<sub>e': 'Ln',
  'Log<sub>e10': 'Log 10',
  'Log<sub> N': 'Log N',
  '1/n': 'Inverse',
  'N<sup>2</sup>': 'Square',
  'N<sup>3</sup>': 'Cube',
  'N<sup>y': 'Power',
  '√n': 'Square Root',
  'N√x': 'Nth Root',
  '+1': 'Plus One',
  '-1': 'Minus One',
  '-N': 'Negate',
  '1-N': 'One Minus',
  
  'Ease  In/ Out Rebound': 'Ease In Out Rebound',
  'Ease In/ Out Bounce': 'Ease In Out Bounce',
  'Ease In/ Out Circular': 'Ease In Out Circular',
  'Ease In/ Out Cubic': 'Ease In Out Cubic',
  'Ease In/ Out Elastic': 'Ease In Out Elastic',
  'Ease In/ Out Exponential': 'Ease In Out Exponential',
  'Ease In/ Out Quadratic': 'Ease In Out Quadratic',
  'Ease In/ Out Quartic': 'Ease In Out Quartic',
  'Ease In/ Out Quintic': 'Ease In Out Quintic',
  'Ease In/ Out Sine': 'Ease In Out Sine',
  
  'Smooth 1/d T': 'Smooth Inverse dT',
  'T <size=25%>(double)': 'World Time As Double',
  'T*10': 'Ten World Time',
  'T*2': 'Double World Time',
  'T/10': 'Tenth World Time',
  'T/2': 'Half World Time',
  '÷d T': 'Divide dT',
  '*d T': 'Multiply dT',
  
  '| V|': 'Vector Magnitude',
  '| V|<sup>2</sup>': 'Vector Magnitude Squared',
  '°<br><size=25%>(angle)': 'Vector Angle',
  '⋅<br><size=25%>(dot Product)': 'Vector Dot',
  '×<br><size=25%>(cross Product)': 'Vector Cross',
  'M<sup> 1</sup><br><size=25%>(inverse)': 'Matrix Inverse',
  'M<sup> T</sup><br><size=25%>(transpose)': 'Matrix Transpose',
  
  'Parse Quantity`1': 'Parse Quantity',
  'From Base Value`1': 'Quantity From Base Value',
  'Base Value`1': 'Quantity To Base Value',
  'Format Quantity`1': 'Format Quantity',
  
  'Delete Dynamic Variable`1': 'Delete Dynamic Variable',
  'Clear Dynamic Variables Of Type`1': 'Clear Dynamic Variables Of Type',
  
  'Object Field Drive`1': '-- object field drive',
  'Reference Drive`1': '-- reference drive',
  'Value Field Drive`1': '-- value field drive',
  
  'Previous Value`1': 'Enum Previous',
  'Next Value`1': 'Enum Next',
  'Shift Enum`1': 'Enum Shift',
  'Random Enum`1': 'Enum Random',
  
  '<color=red>b<color=orange>o<color=yellow>b<color=lime>o<color=cyan>o<color=blue>l<color=purple>3<color=magenta>o<color=red>l': 'bobool3ol',
  'Is ∞': 'Is Infinite',
  '?:': 'Ternary',
  '??': 'Coalesce',
  'Field As Variable`1': 'IValue As Variable',
  'Get Asset`1': 'Get Asset',
  'Lerp (unclamped)': 'Lerp Unclamped',
  'Reference Target`1': 'Reference Target',
  'Sample Min/ Max Spatial Var': 'Sample Min Max Spatial Var',
  'Sample Object Animation Track`1': 'Sample Object Animation Track',
  'Sample Value Animation Track`1': 'Sample Value Animation Track',
}

concrete = [(typ, meta, path, rename.get(name, name)) for typ,meta,path,name in concrete]
generic1 = [(typ, meta, path, rename.get(name, name)) for typ,meta,path,name in generic1]

# what are my groups?
# simple nodes - no generics - no references - no dynamics - any number of values
#   non impulse
#   max one impulse
# non simple nodes </3

class TestEq:
  def __init__(self, test):
    self.test = test
  
  def __eq__(self, other):
    return self.test(other)

Any = TestEq(lambda x: True)
Ge = lambda v: TestEq(lambda x: x >= v)

def getsignature(nodedata):
  typ,meta,path,name = nodedata
  FixedOperationsCount = len(meta.FixedOperations)
  DynamicOperationsCount = len(meta.DynamicOperations)
  FixedInputsCount = len(meta.FixedInputs)
  DynamicInputsCount = len(meta.DynamicInputs)
  FixedImpulsesCount = len(meta.FixedImpulses)
  DynamicImpulsesCount = len(meta.DynamicImpulses)
  FixedOutputsCount = len(meta.FixedOutputs)
  DynamicOutputsCount = len(meta.DynamicOutputs)
  FixedReferencesCount = len(meta.FixedReferences)
  FixedGlobalRefsCount = len(meta.FixedGlobalRefs)
  DynamicGlobalRefsCount = len(meta.DynamicGlobalRefs)
  return (FixedOperationsCount, DynamicOperationsCount, FixedInputsCount, DynamicInputsCount, FixedImpulsesCount, DynamicImpulsesCount, FixedOutputsCount, DynamicOutputsCount, FixedReferencesCount, FixedGlobalRefsCount, DynamicGlobalRefsCount)

def filternodes(nodedatas):
  lists = [[] for _ in range(typescount)]
  for nodedata in nodedatas:
    lists[filternode(nodedata)].append(nodedata)
  print([len(l) for l in lists])
  return lists

def signatures(nodedatas):
  for nodedata in nodedatas:
    typ,meta,path,name = nodedata
    print(getsignature(nodedata), name, typ)

def filternode(nodedata):
  signature = getsignature(nodedata)
  # the bracketed numbers are the counts as of 2025.9.12.1173 resonite
  # of [concrete, generic1]
  if signature == (0, 0, Any, 0, 0, 0, Any, 0, 0, 0, 0):
    return 1 # simple data nodes [2535, 143]
  if signature == (1, 0, Any, 0, 1, 0, Any, 0, 0, 0, 0):
    return 2 # simple linear nodes [99, 4]
  if signature == (0, 0, Any, 0, 1, 0, Any, 0, 0, 0, 0):
    return 3 # events (including call input) (also fire while true and update) [22, 9]
  if signature == (1, 0, Any, 0, 0, 0, Any, 0, 0, 0, 0):
    return 4 # impulse display [2, 1]
  if signature == (1, 0, Any, 0, Any, 0, Any, 0, 0, 0, 0):
    return 5 # operation that may fail (or have some other set of fixed output paths like if or for) [42, 35]
  if signature == (0, 0, Any, 0, 0, 0, Any, 0, 0, 1, 0):
    return 6 # data only node with a reference (a source of some kind) [3, 8]
  if signature == (0, 0, Any, 0, Any, 0, Any, 0, 0, 1, 0):
    return 7 # probably an event node tbh (all of them are) [29, 6]
  if signature == (0, 0, 0, 1, 0, 0, Any, 0, 0, 0, 0):
    return 8 # data node with only a dynamic input list (concrete is all multi operations) [132, 9]
  if signature == (0, 0, Ge(1), 1, 0, 0, Any, 0, 0, 0, 0):
    return 9 # data node with a dynamic input list and some fixed inputs (concrete is all multi operations except for format string) [52, 5]
  if signature == (Any, Any, Any, Any, Any, Any, Any, Ge(1), Any, Any, Any):
    return 10 # dynamic output [0, 3]
  if signature == (Any, Any, Any, Any, Any, Any, Any, Any, Ge(1), Any, Any):
    return 11 # static reference (all of these i don't want to do </3 - the generic ones (all of them except Link) probably aren't that bad though) [1, 7]
  return 0 # random stuff [15, 4]

typescount = 12

concretesplit = filternodes(concrete)
generic1split = filternodes(generic1)

(
  concreteother, # 2 global refs (updatinguser + skipifnull), advanced flow control tm (sequence, multiplex, pulse random), other nodes with multiple impulse inputs
  concretesimple, # no impulses, no references - can be used anywhere
  concretelinear, # one impulse in, one impulse out, no references - can also be used anywhere
  concreteisource, # events without reference (they all have one impulse output) (includes fire on true and friends)
  concreteidest, # pulse display and "test feature upgrade" (why)
  concreteflow, # mostly operations with multiple output paths, but also includes some control flow (if, while, for, delay)
  concretevsource, # changeablesource
  concreteevents, # events (all have references)
  concretepuremulti, # multi operations (these are mostly boolean/bitwise but there's concatenate and average as well)
  concretemulti, # multi operations with fixed inputs (string format and join and various lerp)
  _, # nothing here
  _, # link
) = concretesplit

(
  generic1other, # field hook and write latch (both have multiple impulse inputs)
  generic1simple, # has enum handling, comparison and operators, spatial variables, and others
  generic1linear, # dynamic impulse trigger with data
  generic1isource, # has call (need context type), fire on local true/false (need context type, overshadowed by concrete one), and fire on change/local change
  generic1idest, # pulse display (overshadowed by the concrete one)
  generic1flow, # delay with data, dynamic/cloud variable, and tween
  generic1vsource, # sources (changeable, reference, data), global to output, and dynamic variable input
  generic1events, # dynamic variable input with events and dynamic impulse reciever with data
  generic1puremulti, # multi operations, pick random, and null coalesce
  generic1multi, # multiplex, index of first match, lerp
  generic1demultiplex, # also nest but nah
  generic1gref, # global reference (oh no two tags)
) = generic1split