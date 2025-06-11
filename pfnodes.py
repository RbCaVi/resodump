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
    'continuations': True, # a node with continuations: True must have named output arguments and a continuation out called Next
    'in': [['Slot', 'Template'], ['Slot', 'OverrideParent']],
    'out': [['Slot', 'Duplicate']],
  },
  ('Dynamic', 'Impulse', 'Trigger'): {
    'continuations': True,
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
    'continuations': ['LoopEnd', ['LoopStart', 'LoopIteration']], # LoopEnd connects to the next statement
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
    'continuations': [True, ['OnTrue', 'OnFalse']], # both branches connect to the next statement
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
  ('Max',): [ # list means try any of these
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
  ('Mul',): {
    'tag': 'type',
    'in': [['$', 'A'], ['$', 'B']],
    'out': '$',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMul',
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
    'continuations': [False, ['Equipped', 'Dequipped', 'ToolUpdate', 'PrimaryPressed', 'PrimaryHeld', 'PrimaryReleased', 'SecondaryPressed', 'SecondaryHeld', 'SecondaryReleased']], # no branches connect to the next statement
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
    'continuations': True,
    'in': [['Slot', 'Instance'], ['float3', 'Position']],
    'out': [],
  },
  ('Set', 'Local', 'Scale'): {
    'continuations': True,
    'in': [['Slot', 'Instance'], ['float3', 'Scale']],
    'out': [],
  },
  ('Set', 'Parent'): {
    'continuations': True,
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
    'continuations': ['OnSuccess', ['OnNotFound', 'OnFailed']], # i'm assuming you would want to continue from OnSuccess usually
    'in': [['Slot', 'Target'], ['string', 'Path'], ['$', 'Value']],
    'out': [],
  },
  ('Return',): {
    'continuations': 'builtin', # return a value from a block # builtin, not a real node
  },
  ('Function',): {
    'continuations': 'builtin', # define a function that is used with an impulse multiplexer/demultiplexer
  },
  ('Continue',): {
    'continuations': 'builtin', # return current impulse explicitly
  },
  ('Join',): {
    'continuations': 'builtin', # join two impulses into one - like impulse multiplexer with no index
  },
  ('Impulse', 'Multiplexer'): {
    'continuations': 'builtin', # special handling
  },
  ('Impulse', 'Demultiplexer'): {
    'continuations': 'builtin', # special handling
  },
}

def getnode(name):
  # will add node aliases eventually
  return nodes[tuple(name)]