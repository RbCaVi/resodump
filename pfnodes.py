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
  ('Conditional'): {
    'tag': 'type', # a type tag is also added to the node type
    'in': [['$', 'OnTrue'], ['$', 'OnFalse'], ['bool', 'Condition']],
    'out': '$',
  },
  ('Div'): {
    'tag': 'type',
    'in': ['$', '$'],
    'out': '$',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueDiv',
  },
  ('Duplicate', 'Slot'): {
    'continuations': True,
    'in': ['Slot', 'Slot'],
    'out': 'Slot',
  },
  ('Dynamic', 'Impulse', 'Trigger'): {
    'continuations': true,
    'in': ['string', 'Slot', 'bool'],
    'out': 'int',
  },
  ('Find', 'Child', 'By', 'Name'): {
    'in': ['Slot', 'string', 'int'],
    'out': 'Slot',
  },
  ('Find', 'Child', 'By', 'Tag'): {
    'in': ['Slot', 'string', 'bool', 'bool', 'int'],
    'out': 'Slot',
  },
  ('For'): {
    'continuations': ['LoopEnd', ['LoopStart', 'LoopIteration']], # LoopEnd connects to the next statement
    'in': ['int', 'bool'],
    'out': 'int',
  },
  ('Get', 'Active', 'User', 'Self'): {
    'in': [],
    'out': 'User',
  },
  ('Get', 'Child'): {
    'in': ['Slot', 'int'],
    'out': 'Slot',
  },
  ('Get', 'Side'): {
    'in': ['BodyNode', 'Chirality'],
    'out': 'BodyNode',
  },
  ('Get', 'Slot'): {
    'in': ['Component'],
    'out': 'Slot',
  },
  ('Get', 'User', 'Grabber'): {
    'in': ['User', 'BodyNode'],
    'out': 'Grabber',
  },
  ('If'): {
    'continuations': [True, ['OnTrue', 'OnFalse']], # both branches connect to the next statement
    'in': ['bool'],
    'out': [],
  },
  ('Local', 'Transform'): {
    'in': ['Slot'],
    'out': ['float3', 'floatq', 'float3'],
  },
  ('Min'): {
    'tag': 'type',
    'in': ['$', '$'],
    'out': '$',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMin',
  },
  ('Max'): [ # list means try any of these
    {
      'tag': 'type',
      'in': ['$', '$'],
      'out': '$',
      'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMax',
    },
    {
      'tag': 'type',
      'in': ['*$'], # * means list of inputs
      'out': '$',
      'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMaxMulti',
    },
  ],
  ('Mul'): {
    'tag': 'type',
    'in': ['$', '$'],
    'out': '$',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.ValueMul',
  },
  ('NOT'): {
    'in': ['bool'],
    'out': 'bool',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.NOT_bool',
  },
  ('Not', 'Null'): {
    'tag': 'type',
    'in': ['$'],
    'out': 'bool',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.NotNull',
  },
  ('RawDataTool', 'Events'): {
    'tag': ['ref', 'RawDataTool', 'Tool'], # type RawDataTool, name Tool # will have a GlobalReference to a RawDataTool
    'continuations': [False, ['Equipped', 'Dequipped', 'ToolUpdate', 'PrimaryPressed', 'PrimaryHeld', 'PrimaryReleased', 'SecondaryPressed', 'SecondaryHeld', 'SecondaryReleased']], # no branches connect to the next statement
    'in': [],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Interaction.Tools.RawDataToolEvents',
  },
  ('Read', 'Dynamic', 'Variable'): {
    'tag': 'type',
    'in': ['Slot', 'string'],
    'out': ['bool', '$'],
    'node': { # use a different node depending on if the type is a value type or an object type
      '$object': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.ReadDynamicObjectVariable',
      '$value': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.ReadDynamicValueVariable',
    }
  },
  ('Set', 'Local', 'Position'): {
    'continuations': True,
    'in': ['Slot', 'float3'],
    'out': [],
  },
  ('Set', 'Local', 'Scale'): {
    'continuations': True,
    'in': ['Slot', 'float3'],
    'out': [],
  },
  ('Set', 'Parent'): {
    'continuations': True,
    'in': ['Slot', 'Slot', 'bool'],
    'out': [],
  },
  ('Tool', 'Equipping', 'Side'): {
    'in': ['Tool'],
    'out': 'Chirality',
  },
  ('Unpack', 'xyz'): {
    'in': ['float3'],
    'out': ['float', 'float', 'float'],
  },
  ('User', 'Root', 'Slot'): {
    'in': ['User'],
    'out': 'Slot',
  },
  ('Write', 'Dynamic', 'Variable'): {
    'tag': 'type',
    'continuations': ['OnSuccess', ['OnNotFound', 'OnFailed']], # i'm assuming you would want to continue from OnSuccess usually
    'in': ['Slot', 'string', '$'],
    'out': [],
  },
}