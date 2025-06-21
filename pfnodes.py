nodes = {
  ('Bounding', 'Box', 'Properties'): {
    'in': [['BoundingBox', 'Bounds']],
    'out': [['float3', 'Min'], ['float3', 'Max'], ['float3', 'Center'], ['float3', 'Size'], ['bool', 'Valid'], ['bool', 'Empty']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Math.Bounds.BoundingBoxProperties',
  },
  ('Children', 'Count'): {
    'in': [['Slot', 'Instance']],
    'out': 'int',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.ChildrenCount',
  },
  ('Compute', 'Bounding', 'Box'): {
    'in': [['Slot', 'Instance'], ['bool', 'IncludeInactive'], ['Slot', 'CoordinateSpace'], ['string', 'OnlyWithTag']],
    'out': 'BoundingBox',
    'node':'[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Math.Bounds.ComputeBoundingBox',
  },
  ('Conditional',): {
    'tag': 'type', # a type tag is also added to the node type
    'in': [['$', 'OnTrue'], ['$', 'OnFalse'], ['bool', 'Condition']],
    'out': '$',
    'node': { # use a different node depending on if the type is a value type or an object type
      '$object': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.ObjectConditional',
      '$value': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.ValueConditional',
    }
  },
  ('Destroy', 'Slot'): {
    'impulses': True, # a node with impulses: True must have named output arguments and an impulse out called Next
    'in': [['Slot', 'Instance'], ['bool', 'PreserveAssets'], ['bool', 'SendDestroyingEvent']],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.DestroySlot',
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
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.DuplicateSlot',
  },
  ('Dynamic', 'Impulse', 'Reciever'): {
    'tag': ['string', 'Tag'],
    'impulses': [None, ['OnTriggered']],
    'in': [],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Actions.DynamicImpulseReceiver',
  },
  ('Dynamic', 'Impulse', 'Trigger'): {
    'impulses': True,
    'in': [['string', 'Tag'], ['Slot', 'TargetHierarchy'], ['bool', 'ExcludeDisabled']],
    'out': [['int', 'TriggeredCount']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Actions.DynamicImpulseTrigger',
  },
  ('Dynamic', 'Variable', 'Input'): {
    'tag': ['string', 'VariableName'],
    'in': [],
    'out': [['$', 'Value'], ['bool', 'HasValue']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Actions.DynamicVariableInput',
  },
  ('Find', 'Child', 'By', 'Name'): {
    'in': [['Slot', 'Instance'], ['string', 'Name'], ['bool', 'MatchSubstring'], ['bool', 'IgnoreCase'], ['int', 'SearchDepth']],
    'out': 'Slot',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.FindChildByName',
  },
  ('Find', 'Child', 'By', 'Tag'): {
    'in': [['Slot', 'Instance'], ['string', 'Tag'], ['int', 'SearchDepth']],
    'out': 'Slot',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.FindChildByTag',
  },
  ('For',): {
    'impulses': ['LoopEnd', ['LoopStart', 'LoopIteration', 'LoopEnd']], # LoopEnd connects to the next statement
    'in': [['int', 'Count'], ['bool', 'Reverse']],
    'out': [['int', 'Iteration']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.For',
  },
  ('Get', 'Active', 'User', 'Self'): {
    'in': [],
    'out': 'User',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.GetActiveUserSelf',
  },
  ('Get', 'Child'): {
    'in': [['Slot', 'Instance'], ['int', 'ChildIndex']],
    'out': 'Slot',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.GetChild',
  },
  ('Get', 'Side'): {
    'in': [['BodyNode', 'Node'], ['Chirality', 'Side']],
    'out': 'BodyNode',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Avatar.BodyNodes.GetSide',
  },
  ('Get', 'Slot'): {
    'in': [['Component', 'Component']],
    'out': 'Slot',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.GetSlot',
  },
  ('Get', 'User', 'Grabber'): {
    'in': [['User', 'User'], ['BodyNode', 'Node']],
    'out': 'Grabber',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Interaction.GetUserGrabber',
  },
  ('If',): {
    'impulses': [True, ['OnTrue', 'OnFalse']], # both branches connect to the next statement
    'in': [['bool', 'Condition']],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.If',
  },
  ('Local', 'Transform'): {
    'in': [['Slot', 'Instance']],
    'out': [['float3', 'LocalPosition'], ['floatq', 'LocalRotation'], ['float3', 'LocalScale']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Transform.LocalTransform',
  },
  ('Min',): {
    'tag': 'type',
    'in': [['$', 'A'], ['$', 'B']],
    'out': '$',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Math.ValueMin',
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
        'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Math.ValueMaxMulti',
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
        'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.Mul_Float_Float3',
      },
    ],
  },
  ('Multiplex',): {
    'tag': 'type',
    'in': [['int', 'Index'], ['*$', 'Inputs']], # * means list of inputs
    'out': '$',
    'node': { # use a different node depending on if the type is a value type or an object type
      '$object': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.ObjectMultiplex',
      '$value': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.ValueMultiplex',
    }
  },
  ('NOT',): {
    'in': [['bool', 'A']],
    'out': 'bool',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.NOT_Bool',
  },
  ('Not', 'Null'): {
    'tag': 'type',
    'in': [['$', 'Instance']],
    'out': 'bool',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.NotNull',
  },
  ('Pack', 'xyz'): {
    'in': [['float', 'X'], ['float', 'Y'], ['float', 'Z']],
    'out': 'float3',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.Pack_Float3',
  },
  ('RawDataTool', 'Events'): {
    'tag': ['RawDataTool', 'Tool'], # type RawDataTool, name Tool # will have a GlobalReference<RawDataTool> component
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
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Transform.SetLocalPosition',
  },
  ('Set', 'Local', 'Scale'): {
    'impulses': True,
    'in': [['Slot', 'Instance'], ['float3', 'Scale']],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Transform.SetLocalScale',
  },
  ('Set', 'Parent'): {
    'impulses': True,
    'in': [['Slot', 'Instance'], ['Slot', 'NewParent'], ['bool', 'PreserveGlobalPosition']],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.SetParent',
  },
  ('Set', 'Slot', 'Active', 'Self'): {
    'impulses': True,
    'in': [['Slot', 'Instance'], ['bool', 'Active']],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.SetSlotActiveSelf',
  },
  ('Slot', 'Children', 'Events'): {
    'tag': ['Slot', 'Instance'], # type Slot, name Instance # will have a GlobalReference<Slot> component
    'impulses': [None, ['OnChildAdded', 'OnChildRemoved']], # no branches connect to the next statement # also no impulse input
    'in': [['User', 'OnUser']],
    'out': [['Slot', 'Child']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Slots.SlotChildrenEvents',
  },
  ('Tool', 'Equipping', 'Side'): {
    'in': [['Tool', 'Tool']],
    'out': 'Chirality',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Interaction.Tools.ToolEquippingSide',
  },
  ('Unpack', 'xyz'): {
    'in': [['float3', 'V']],
    'out': [['float', 'X'], ['float', 'Y'], ['float', 'Z']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Operators.Unpack_Float3',
  },
  ('User', 'Root', 'Slot'): {
    'in': [['User', 'User']],
    'out': 'Slot',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Users.UserRootSlot',
  },
  ('Write', 'Dynamic', 'Variable'): {
    'tag': 'type',
    'impulses': ['OnSuccess', ['OnSuccess', 'OnNotFound', 'OnFailed']], # i'm assuming you would want to continue from OnSuccess usually
    'in': [['Slot', 'Target'], ['string', 'Path'], ['$', 'Value']],
    'out': [],
    'node': { # use a different node depending on if the type is a value type or an object type
      '$object': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.WriteDynamicObjectVariable',
      '$value': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.FrooxEngine.Variables.WriteDynamicValueVariable',
    }
  },
  ('Continue',): {
    'impulses': True, # return current impulse explicitly
  },
  # i'll deal with these in their own way
  # because they have varying numbers of impulse inputs/outputs
  ('Impulse', 'Multiplexer'): {
    'impulses': 'builtin',
    'impulsein': True,
    'impulseout': [], # has a list of impulses
    'in': [['int', 'Index']],
    'out': [],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.ImpulseMultiplexer',
  },
  ('Impulse', 'Demultiplexer'): {
    'impulses': 'builtin',
    'impulsein': False, # has a list of impulses
    'impulseout': [['OnTriggered', True]],
    'in': [],
    'out': [['int', 'Index']],
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.ImpulseDemultiplexer',
  },
  ('Cast',): {
    'impulses': 'builtin',
    'in': [['_', 'Input']],
    'out': '_',
    'node': '[ProtoFluxBindings]FrooxEngine.ProtoFlux.Runtimes.Execution.Nodes.Casts.',
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

def fixnode(node, name):
  node['name'] = name
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

for name,node in nodes.items():
  fixnode(node, name)

def getnode(name):
  # will add node aliases eventually
  return nodes[tuple(name)]