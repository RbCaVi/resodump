nodes = {
  ('Bounding', 'Box', 'Properties'): {
    'in': [['BoundingBox', 'Bounds']],
    'out': [['float3', 'Min'], ['float3', 'Max'], ['float3', 'Center'], ['float3', 'Size'], ['bool', 'Valid'], ['bool', 'Empty']],
  },
  ('Children', 'Count'): {
    'in': [['Slot', 'Instance']],
    'out': 'int',
  },
  ('Compute', 'Bounding', 'Box'): {
    'in': [['Slot', 'Instance'], ['bool', 'IncludeInactive'], ['Slot', 'CoordinateSpace'], ['string', 'OnlyWithTag']],
    'out': 'BoundingBox',
  },
  ('Conditional',): {
    'tag': 'type', # a type tag is also added to the node type
    'in': [['$', 'OnTrue'], ['$', 'OnFalse'], ['bool', 'Condition']],
    'out': '$',
  },
  ('Div',): {
    'tag': 'type',
    'in': [['$', 'A'], ['$', 'B']],
    'out': '$',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueDiv',
  },
  ('Duplicate', 'Slot'): {
    'impulses': True, # a node with impulses: True must have named output arguments and an impulse out called Next
    'in': [['Slot', 'Template'], ['Slot', 'OverrideParent']],
    'out': [['Slot', 'Duplicate']],
  },
  ('Dynamic', 'Impulse', 'Trigger'): {
    'impulses': True,
    'in': [['string', 'Tag'], ['Slot', 'TargetHierarchy'], ['bool', 'ExcludeDisabled']],
    'out': 'int',
  },
  ('Find', 'Child', 'By', 'Name'): {
    'in': [['Slot', 'Instance'], ['string', 'Name'], ['bool', 'MatchSubstring'], ['bool', 'IgnoreCase'], ['int', 'SearchDepth']],
    'out': 'Slot',
  },
  ('Find', 'Child', 'By', 'Tag'): {
    'in': [['Slot', 'Instance'], ['string', 'Tag'], ['int', 'SearchDepth']],
    'out': 'Slot',
  },
  ('For',): {
    'impulses': ['LoopEnd', ['LoopStart', 'LoopIteration', 'LoopEnd']], # LoopEnd connects to the next statement
    'in': [['int', 'Count'], ['bool', 'Reverse ']],
    'out': [['int', 'iteration']],
  },
  ('Get', 'Active', 'User', 'Self'): {
    'in': [],
    'out': 'User',
  },
  ('Get', 'Child'): {
    'in': [['Slot', 'Instance'], ['int', 'ChildIndex']],
    'out': 'Slot',
  },
  ('Get', 'Side'): {
    'in': [['BodyNode', 'Node'], ['Chirality', 'Side']],
    'out': 'BodyNode',
  },
  ('Get', 'Slot'): {
    'in': [['Component', 'Component']],
    'out': 'Slot',
  },
  ('Get', 'User', 'Grabber'): {
    'in': [['User', 'User'], ['BodyNode', 'Node']],
    'out': 'Grabber',
  },
  ('If',): {
    'impulses': [True, ['OnTrue', 'OnFalse']], # both branches connect to the next statement
    'in': [['bool', 'Condition']],
    'out': [],
  },
  ('Local', 'Transform'): {
    'in': [['Slot', 'Instance']],
    'out': [['float3', 'Position'], ['floatq', 'Rotation'], ['float3', 'Scale']],
  },
  ('Min',): {
    'tag': 'type',
    'in': [['$', 'A'], ['$', 'B']],
    'out': '$',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMin',
  },
  ('Max',): {
    'forms': [ # max has multiple forms # so do mul and min, but i was lazy to do them
      {
        'tag': 'type',
        'in': [['$', 'A'], ['$', 'B']],
        'out': '$',
        'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMax',
      },
      {
        'tag': 'type',
        'in': [['*$', 'Operands']], # * means list of inputs
        'out': '$',
        'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMaxMulti',
      },
    ],
  },
  ('Mul',): {
    'forms': [
      {
        'tag': 'type',
        'in': [['$', 'A'], ['$', 'B']],
        'out': '$',
        'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMul',
      },
      {
        'in': [['float', 'A'], ['float3', 'B']],
        'out': 'float3',
      },
    ],
  },
  ('NOT',): {
    'in': [['bool', 'A']],
    'out': 'bool',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.NOT_bool',
  },
  ('Not', 'Null'): {
    'tag': 'type',
    'in': [['$', 'Instance']],
    'out': 'bool',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.NotNull',
  },
  ('RawDataTool', 'Events'): {
    'tag': ['ref', 'RawDataTool', 'Tool'], # type RawDataTool, name Tool # will have a GlobalReference<RawDataTool> component
    'impulses': [None, ['Equipped', 'Dequipped', 'ToolUpdate', 'PrimaryPressed', 'PrimaryHeld', 'PrimaryReleased', 'SecondaryPressed', 'SecondaryHeld', 'SecondaryReleased']], # no branches connect to the next statement # also no impulse input
    'in': [],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Interaction.Tools.RawDataToolEvents',
  },
  ('Read', 'Dynamic', 'Variable'): {
    'tag': 'type',
    'in': [['Slot', 'Source'], ['string', 'Path']],
    'out': [['bool', 'FoundValue'], ['$', 'Value']],
    'node': { # use a different node depending on if the type is a value type or an object type
      '$object': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.ReadDynamicObjectVariable',
      '$value': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.ReadDynamicValueVariable',
    }
  },
  ('Set', 'Local', 'Position'): {
    'impulses': True,
    'in': [['Slot', 'Instance'], ['float3', 'Position']],
    'out': [],
  },
  ('Set', 'Local', 'Scale'): {
    'impulses': True,
    'in': [['Slot', 'Instance'], ['float3', 'Scale']],
    'out': [],
  },
  ('Set', 'Parent'): {
    'impulses': True,
    'in': [['Slot', 'Instance'], ['Slot', 'NewParent'], ['bool', 'PreserveGlobalPosition']],
    'out': [],
  },
  ('Tool', 'Equipping', 'Side'): {
    'in': [['Tool', 'Tool']],
    'out': 'Chirality',
  },
  ('Unpack', 'xyz'): {
    'in': [['float3', '']],
    'out': [['float', ''], ['float', ''], ['float', '']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.Unpack_Float3',
  },
  ('User', 'Root', 'Slot'): {
    'in': [['User', 'User']],
    'out': 'Slot',
  },
  ('Write', 'Dynamic', 'Variable'): {
    'tag': 'type',
    'impulses': ['OnSuccess', ['OnSuccess', 'OnNotFound', 'OnFailed']], # i'm assuming you would want to continue from OnSuccess usually
    'in': [['Slot', 'Target'], ['string', 'Path'], ['$', 'Value']],
    'out': [],
  },
  ('Continue',): {
    'impulses': True, # return current impulse explicitly
  },
  # i'll deal with these in their own way
  # because they have varying numbers of impulse inputs/outputs
  ('Impulse', 'Multiplexer'): {
    'impulses': 'builtin',
    'in': [['int', 'Index']],
    'out': [],
  },
  ('Impulse', 'Demultiplexer'): {
    'impulses': 'builtin',
    'in': [],
    'out': [['int', 'Index']],
  },
  ('Join',): {
    'impulses': 'builtin', # join two impulses into one - like impulse demultiplexer with no index
  },
  ('Return',): {
    'impulses': 'builtin', # return a value from a block # does not have an impulse output?
    'impulsein': True,
    'impulseout': [],
  },
  ('Function',): {
    'impulses': 'builtin', # define a function # implemented with an impulse multiplexer/demultiplexer
  },
}

def fixnodeimpulses(node):
  if 'impulses' not in node:
    return
  impulses = node['impulses']
  if impulses == 'builtin':
    node['builtin'] = True
    node['linear'] = False
    return
  if impulses == True:
    node['impulsein'] = True
    node['impulseout'] = [['Next', True]]
    node['linear'] = True
    return
  if impulses[0] == None:
    node['impulsein'] = False
    node['impulseout'] = [[iname, False] for iname in impulses[1]]
    node['linear'] = False
    return
  if impulses[0] == False:
    node['impulsein'] = True
    node['impulseout'] = [[iname, False] for iname in impulses[1]]
    node['linear'] = False
    return
  if impulses[0] == True:
    node['impulsein'] = True
    node['impulseout'] = [[iname, True] for iname in impulses[1]]
    node['linear'] = False
    return
  node['impulsein'] = True
  node['impulseout'] = [[iname, iname == impulses[0]] for iname in impulses[1]]
  node['linear'] = False
  return

for node in nodes.values():
  fixnodeimpulses(node)

def getnode(name):
  # will add node aliases eventually
  return nodes[tuple(name)]