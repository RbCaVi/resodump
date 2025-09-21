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

import pf_metadata

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
  # these are never getting real
  'FrooxEngine.ProtoFlux.CoreNodes.AsyncMethodProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.AsyncValueFunctionProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.AsyncObjectFunctionProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.SyncMethodProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.SyncValueFunctionProxy',
  'FrooxEngine.ProtoFlux.CoreNodes.SyncObjectFunctionProxy',
  'ProtoFlux.Runtimes.Execution.NestedNode',
  'ProtoFlux.Runtimes.Execution.Nodes.Link',
  'ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Debugging.TestFeatureUpgrade',
  'ProtoFlux.Runtimes.DSP.Array.',
  'ProtoFlux.Core.ImpulseExportNode',
  'ProtoFlux.Core.DataImportNode',
  'ProtoFlux.Runtimes.Execution.Nodes.ValueConstant',
  'ProtoFlux.Runtimes.Execution.Nodes.ObjectConstant',
  
  # i'm planning to have these as specially handled nodes
  # dynamic numbers of impulses
  # value and impulse sources (automatically inserted)
  'ProtoFlux.Runtimes.Execution.Nodes.ImpulseDemultiplexer',
  'ProtoFlux.Runtimes.Execution.Nodes.ImpulseMultiplexer',
  'ProtoFlux.Runtimes.Execution.Nodes.AsyncSequence',
  'ProtoFlux.Runtimes.Execution.Nodes.Actions.PulseRandom',
  'ProtoFlux.Runtimes.Execution.Nodes.Sequence',
  
  'FrooxEngine.ProtoFlux.CoreNodes.SlotSource',
  'FrooxEngine.ProtoFlux.CoreNodes.SlotRefSource',
  'FrooxEngine.ProtoFlux.CoreNodes.UserRefSource',
  'FrooxEngine.ProtoFlux.CoreNodes.ElementSource',
  'FrooxEngine.ProtoFlux.CoreNodes.ReferenceSource',
  'FrooxEngine.ProtoFlux.CoreNodes.ValueSource',
  'FrooxEngine.ProtoFlux.CoreNodes.ObjectValueSource',
  
  'ProtoFlux.Runtimes.Execution.Nodes.ExternalCall',
  'ProtoFlux.Runtimes.Execution.Nodes.ExternalAsyncCall',
]])]

typedatas = [(
  t,
  metadata := pf_metadata.ProcessNodeMetadata(NodeMetadataHelper.GetMetadata(t)),
  nullconcat('Root/', getoptionalname(firstornone(t.GetCustomAttributes(NodeCategoryAttribute, True)))) or 'Root',
  metadata.Name or StringHelper.BeautifyName(metadata.Overload or t.Name), # the metadata.Overload field is (right now) always overshadowed by metadata.Name
) for t in types]

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
  
  '+': 'Add', # or concat for strings
  '-': 'Subtract',
  '±': 'Add Subtract',
  '×': 'Multiply', # or repeat for strings
  '÷': 'Divide',
  '%': 'Modulo',
  '<<': 'Shift Left',
  '>>': 'Shift Right',
  
  '++': 'Increment',
  '--': 'Decrement',
  
  'τ': 'Tau',
  'π': 'Pi',
  'π/2': 'Half Pi',
  'π/4': 'Quarter Pi',
  '1/τ': 'Inverse Tau',
  '1/π': 'Inverse Pi',
  '1/(π/2)': 'Inverse Half Pi',
  '1/(π/4)': 'Inverse Quarter Pi',
  'ϕ': 'Phi',
  
  '==': 'Equal',
  '!=': 'Not Equal',
  '≈': 'Approximately Equal',
  '!≈': 'Not Approximately Equal',
  '<': 'Less Than',
  '>': 'Greater Than',
  '≤': 'Less Than Or Equal',
  '≥': 'Greater Than Or Equal',
  
  "' '<size=25%>(Space)": 'Space Character',
  '\\\\a<size=25%>(Bell)': 'Bell Character',
  '\\\\b<size=25%>(Backspace)': 'Backspace Character',
  '\\\\f<size=25%>(Form Feed)': 'Form Feed Character',
  '\\\\n<size=25%>(NewLine)': 'Newline Character',
  'NewLine (OS)': 'OS Newline Character',
  '\\\\r<size=25%>(Carridge Return)': 'Carriage Return Character',
  '\\\\t<size=25%>(Tab)': 'Tab Character',
  '\\\\v<size=25%>(Vertical Tab)': 'Vertical Tab Character',
  
  'Sin<sup>-1': 'Arcsin',
  'Cos<sup>-1': 'Arccos',
  'Tan<sup>-1': 'Arctan',
  'e<sup>n': 'Exp',
  'Log<sub>e': 'Ln',
  'Log<sub>e10': 'Log',
  'Log<sub>N': 'Log N',
  '1/n': 'Inverse',
  'n<sup>2</sup>': 'Square',
  'n<sup>3</sup>': 'Cube',
  'n<sup>y': 'Power',
  '√n': 'Square Root',
  'n√x': 'Nth Root',
  '+1': 'Plus One',
  '-1': 'Minus One',
  '-n': 'Negate',
  '1-n': 'One Minus',
  
  'Ease-In Bounce': 'Ease In Bounce',
  'Ease-In Circular': 'Ease In Circular',
  'Ease-In Cubic': 'Ease In Cubic',
  'Ease-In Elastic': 'Ease In Elastic',
  'Ease-In Exponential': 'Ease In Exponential',
  'Ease-In Quadratic': 'Ease In Quadratic',
  'Ease-In Quartic': 'Ease In Quartic',
  'Ease-In Quintic': 'Ease In Quintic',
  'Ease-In Rebound': 'Ease In Rebound',
  'Ease-In Sine': 'Ease In Sine',
  'Ease-In/Out Bounce': 'Ease In Out Bounce',
  'Ease-In/Out Circular': 'Ease In Out Circular',
  'Ease-In/Out Cubic': 'Ease In Out Cubic',
  'Ease-In/Out Elastic': 'Ease In Out Elastic',
  'Ease-In/Out Exponential': 'Ease In Out Exponential',
  'Ease-In/Out Quadratic': 'Ease In Out Quadratic',
  'Ease-In/Out Quartic': 'Ease In Out Quartic',
  'Ease-In/Out Quintic': 'Ease In Out Quintic',
  'Ease- In/Out Rebound': 'Ease In Out Rebound',
  'Ease-In/Out Sine': 'Ease In Out Sine',
  'Ease-Out Bounce': 'Ease Out Bounce',
  'Ease-Out Circular': 'Ease Out Circular',
  'Ease-Out Cubic': 'Ease Out Cubic',
  'Ease-Out Elastic': 'Ease Out Elastic',
  'Ease-Out Exponential': 'Ease Out Exponential',
  'Ease-Out Quadratic': 'Ease Out Quadratic',
  'Ease-Out Quartic': 'Ease Out Quartic',
  'Ease-Out Quintic': 'Ease Out Quintic',
  'Ease-Out Rebound': 'Ease Out Rebound',
  'Ease-Out Sine': 'Ease Out Sine',
  
  'T <size=25%>(double)': 'World Time',
  'T*10': 'Ten World Time',
  'T*2': 'Double World Time',
  'T/10': 'Tenth World Time',
  'T/2': 'Half World Time',
  '*dT': 'Multiply dT',
  '÷dT': 'Divide dT',
  '1/dT': 'Inverse dT',
  'Smooth 1/dT': 'Smooth Inverse dT',
  
  '|V|': 'Vector Magnitude',
  '|V|<sup>2</sup>': 'Vector Magnitude Squared',
  '°<br><size=25%>(angle)': 'Vector Angle Degrees',
  '⋅<br><size=25%>(dot product)': 'Vector Dot',
  '×<br><size=25%>(cross product)': 'Vector Cross',
  'M<sup>-1</sup><br><size=25%>(inverse)': 'Matrix Inverse',
  'M<sup>T</sup><br><size=25%>(transpose)': 'Matrix Transpose',
  
  #'Parse Quantity`1' ProtoFlux.Runtimes.Execution.Nodes.Math.Quantity.ParseQuantity`1[U],
  #'From Base Value`1' ProtoFlux.Runtimes.Execution.Nodes.Math.Quantity.FromBaseValue`1[U],
  #'Base Value`1' ProtoFlux.Runtimes.Execution.Nodes.Math.Quantity.BaseValue`1[U],
  #'Format Quantity`1' ProtoFlux.Runtimes.Execution.Nodes.Math.Quantity.FormatQuantity`1[U],
  
  #'Delete Dynamic Variable`1' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.DeleteDynamicVariable`1[T],
  #'Clear Dynamic Variables Of Type`1' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.ClearDynamicVariablesOfType`1[T],
  
  #'Value Field Drive`1' FrooxEngine.ProtoFlux.CoreNodes.ValueFieldDrive`1[T],
  #'Object Field Drive`1' FrooxEngine.ProtoFlux.CoreNodes.ObjectFieldDrive`1[T],
  #'Reference Drive`1' FrooxEngine.ProtoFlux.CoreNodes.ReferenceDrive`1[T],
  
  'Previous Value`1': 'Enum Previous',
  'Next Value`1': 'Enum Next',
  'Shift Enum`1': 'Enum Shift',
  'Random Enum`1': 'Enum Random',
  
  '7': 'Feven',
  '<color=red>b<color=orange>o<color=yellow>b<color=lime>o<color=cyan>o<color=blue>l<color=purple>3<color=magenta>o<color=red>l': 'bobool3ol',
  
  'Is ∞': 'Is Infinite',
  '?:': 'Ternary',
  '??': 'Coalesce',
  #'Field As Variable`1' FrooxEngine.ProtoFlux.CoreNodes.FieldAsVariable`1[T],
  #'Get Asset`1' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.GetAsset`1[A],
  #'Lerp (unclamped)' ProtoFlux.Runtimes.Execution.Nodes.Math.ValueLerpUnclamped`1[T],
  #'Reference Target`1' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.References.ReferenceTarget`1[T],
  #'Sample Min/Max SpatialVar' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.SampleMinMaxSpatialVariable`1[T],
  #'Sample Object Animation Track`1' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.SampleObjectAnimationTrack`1[T],
  #'Sample Value Animation Track`1' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.SampleValueAnimationTrack`1[T],
  'Deg 2 Rad': 'Degrees To Radians',
  'Rad 2 Deg': 'Radians To Degrees',
  'Repeat 01': 'Repeat Zero One',
  'Remap11_01': 'Remap1101',
  #'Attach Texture 2D' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.AttachTexture2D
  #'Get Texture 2D Pixel' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.GetTexture2D_Pixel
  #'Get Texture 3D Pixel' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.GetTexture3D_Pixel
  #'Mouse Scroll Delta 2D' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Input.Mouse.MouseScrollDelta2D
  #'Sample Texture 2D UV' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.SampleTexture2D_UV
  #'Sample Texture 2D UVW' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.SampleTexture3D_UVW
  #'Simplex 1D' ProtoFlux.Runtimes.Execution.Nodes.Math.Random.SimplexNoise_1D
  #'Simplex 2D' ProtoFlux.Runtimes.Execution.Nodes.Math.Random.SimplexNoise_2D
  #'Simplex 3D' ProtoFlux.Runtimes.Execution.Nodes.Math.Random.SimplexNoise_3D
  #'Simplex 4D' ProtoFlux.Runtimes.Execution.Nodes.Math.Random.SimplexNoise_4D
  #'Texture 2D Format' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.Texture2D_Format
  #'Texture 3D Format' ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Assets.Texture3D_Format
}

typedatas = [(typ, meta, path, rename.get(name, name)) for typ,meta,path,name in typedatas]

for typ,meta,path,name in typedatas:
  print(str(typ), '=', name, str(meta))

for name in sorted({name for _,_,_,name in typedatas}):
  print(name)
  
  for typ,meta,path,tname in typedatas:
    if tname == name:
      print(' ', path, typ)

# generics
generic = [x for x in typedatas if len(x[0].GetGenericArguments()) != 0]
generic1 = [x for x in generic if len(x[0].GetGenericArguments()) == 1]
generic2 = [x for x in generic if len(x[0].GetGenericArguments()) == 2 and x[0].GetGenericArguments()[0].Name != 'C'] # because there are generic versions of some nodes that take a context type as the first parameter # this is literally spherical harmonics evaluate and object cast
# 2 generic parameters is the max for non proxy nodes (proxy nodes go up to like 7)

concrete = [x for x in typedatas if len(x[0].GetGenericArguments()) == 0]

class TestEq:
  def __init__(self, test):
    self.test = test
  
  def __eq__(self, other):
    return self.test(other)

Any = TestEq(lambda x: True)
Ge = lambda v: TestEq(lambda x: x >= v)

def filternodes(nodedatas):
  lists = [[] for _ in range(typescount)]
  for nodedata in nodedatas:
    lists[filternode(nodedata)].append(nodedata)
  print([len(l) for l in lists])
  return lists

def signatures(nodedatas):
  for nodedata in nodedatas:
    typ,meta,path,name = nodedata
    print(meta.signature(), typ, name)

def filternode(nodedata):
  signature = nodedata[1].signature()
  # the bracketed numbers are the counts as of 2025.9.12.1173 resonite
  # of [concrete, generic1]
  if signature == (0, 0, Any, 0, 0, 0, Any, 0, 0, 0, 0):
    return 1 # simple data nodes [2526, 141]
  if signature == (1, 0, Any, 0, 1, 0, Any, 0, 0, 0, 0):
    return 2 # simple linear nodes [99, 4]
  if signature == (0, 0, Any, 0, 1, 0, Any, 0, 0, 0, 0):
    return 3 # events (including call input) (also fire while true and update) [22, 7]
  if signature == (1, 0, Any, 0, Any, 0, Any, 0, 0, 0, 0):
    return 4 # operation that may fail (or have some other set of fixed output paths like if or for) [43, 36]
  if signature == (0, 0, Any, 0, 0, 0, Any, 0, 0, 1, 0):
    return 5 # data only node with a reference (a source of some kind) [0, 4]
  if signature == (0, 0, Any, 0, Any, 0, Any, 0, 0, 1, 0):
    return 6 # probably an event node tbh (all of them are) [29, 6]
  if signature == (0, 0, 0, 1, 0, 0, Any, 0, 0, 0, 0):
    return 7 # data node with only a dynamic input list (concrete is all multi operations) [132, 9]
  if signature == (0, 0, Ge(1), 1, 0, 0, Any, 0, 0, 0, 0):
    return 8 # data node with a dynamic input list and some fixed inputs (concrete is all multi operations except for format string) [52, 5]
  if signature == (Any, Any, Any, Any, Any, Any, Any, Any, Ge(1), Any, Any):
    return 9 # static reference (all of these i don't want to do </3 - the generic ones (all of them except Link) probably aren't that bad though) [0, 7]
  return 0 # random stuff [10, 6]

typescount = 10

concretesplit = filternodes(concrete)
generic1split = filternodes(generic1)

(
  concreteother, # 2 global refs (updatinguser + skipifnull), other nodes with multiple impulse inputs
  concretesimple, # no impulses, no references
  concretelinear, # one impulse in, one impulse out, no references
  concreteisource, # events without reference (they all have one impulse output) (includes fire on true and friends)
  concreteflow, # operations with multiple output paths (usually pass/fail)
  _, # nothing here
  concreteevents, # events (all have references)
  concretepuremulti, # multi operations (these are mostly boolean/bitwise but there's concatenate and average as well)
  concretemulti, # multi operations with fixed inputs (string format and join and various lerp)
  _, # nothing here
) = concretesplit

(
  generic1other, # field hook and write latch (both have multiple impulse inputs)
  generic1simple, # has enum handling, comparison and operators, spatial variables, and others
  generic1linear, # dynamic impulse trigger with data
  generic1isource, # fire on local true/false (need context type, overshadowed by concrete one) and fire on change/local change
  generic1flow, # delay with data, dynamic/cloud variable, and tween
  generic1vsource, # sources (changeable, reference, data), global to output, and dynamic variable input
  generic1events, # dynamic variable input with events and dynamic impulse reciever with data
  generic1puremulti, # multi operations, pick random, and null coalesce
  generic1multi, # multiplex, index of first match, lerp
  generic1gref, # global reference (oh no two tags)
) = generic1split