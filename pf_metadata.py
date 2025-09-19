def indent(text):
  return '  ' + text.replace('\n', '\n  ')

def lstr(l):
  return '\n'.join(('[',
    *[indent(str(x)) for x in l],
  ']'))

# convert a C# NodeMetadata object into a nested tuple of the data inside it
class ProcessNodeMetadata:
  def __init__(self, meta):
    self.IsPotentiallyListeningToChanges = meta.IsPotentiallyListeningToChanges
    self.FixedInputs = [*map(ProcessInputMetadata, meta.FixedInputs)]
    self.FixedOutputs = [*map(ProcessOutputMetadata, meta.FixedOutputs)]
    self.FixedImpulses = [*map(ProcessImpulseMetadata, meta.FixedImpulses)]
    self.FixedOperations = [*map(ProcessOperationMetadata, meta.FixedOperations)]
    self.FixedReferences = [*map(ProcessReferenceMetadata, meta.FixedReferences)]
    self.FixedGlobalRefs = [*map(ProcessGlobalRefMetadata, meta.FixedGlobalRefs)]
    self.DynamicInputs = [*map(ProcessInputListMetadata, meta.DynamicInputs)]
    self.DynamicOutputs = [*map(ProcessOutputListMetadata, meta.DynamicOutputs)]
    self.DynamicImpulses = [*map(ProcessImpulseListMetadata, meta.DynamicImpulses)]
    self.DynamicOperations = [*map(ProcessOperationListMetadata, meta.DynamicOperations)]
    self.DynamicGlobalRefs = [*map(ProcessGlobalRefListMetadata, meta.DynamicGlobalRefs)]
  
  def __str__(self):
    return '\n'.join(('NodeMetadata {',
      indent('IsPotentiallyListeningToChanges = ' + str(self.IsPotentiallyListeningToChanges)),
      indent('FixedInputs = ' + lstr(self.FixedInputs)),
      indent('FixedOutputs = ' + lstr(self.FixedOutputs)),
      indent('FixedImpulses = ' + lstr(self.FixedImpulses)),
      indent('FixedOperations = ' + lstr(self.FixedOperations)),
      indent('FixedReferences = ' + lstr(self.FixedReferences)),
      indent('FixedGlobalRefs = ' + lstr(self.FixedGlobalRefs)),
      indent('DynamicInputs = ' + lstr(self.DynamicInputs)),
      indent('DynamicOutputs = ' + lstr(self.DynamicOutputs)),
      indent('DynamicImpulses = ' + lstr(self.DynamicImpulses)),
      indent('DynamicOperations = ' + lstr(self.DynamicOperations)),
      indent('DynamicGlobalRefs = ' + lstr(self.DynamicGlobalRefs)),
    '}'))

class ProcessInputMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Field = ProcessFieldInfo(meta.Field)
    self.DefaultValue = meta.DefaultValue
    self.IsConditional = meta.IsConditional
    self.IsListeningToChanges = meta.IsListeningToChanges
    self.IsListeningToChangesEval = ProcessPropertyInfo(meta.IsListeningToChangesEval)
    self.CrossRuntime = ProcessCrossRuntimeInputAttribute(meta.CrossRuntime)
    self.IsPotentiallyListeningToChanges = meta.IsPotentiallyListeningToChanges
    self.DataClass = ProcessDataClass(meta.DataClass)
    self.InputType = ProcessType(meta.InputType)
  
  def __str__(self):
    return '\n'.join(('InputMetadata {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Field = ' + str(self.Field)),
      indent('DefaultValue = ' + str(self.DefaultValue)),
      indent('IsConditional = ' + str(self.IsConditional)),
      indent('IsListeningToChanges = ' + str(self.IsListeningToChanges)),
      indent('IsListeningToChangesEval = ' + str(self.IsListeningToChangesEval)),
      indent('CrossRuntime = ' + str(self.CrossRuntime)),
      indent('IsPotentiallyListeningToChanges = ' + str(self.IsPotentiallyListeningToChanges)),
      indent('DataClass = ' + str(self.DataClass)),
      indent('InputType = ' + str(self.InputType)),
    '}'))

class ProcessOutputMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Field = ProcessFieldInfo(meta.Field)
    self.ChangeTypeEval = ProcessPropertyInfo(meta.ChangeTypeEval)
    self.ChangeType = ProcessOutputChangeSource(meta.ChangeType)
    self.OutputType = ProcessType(meta.OutputType)
    self.DataClass = ProcessDataClass(meta.DataClass)
    self.IsImplicit = meta.IsImplicit
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Field = ' + str(self.Field)),
      indent('ChangeTypeEval = ' + str(self.ChangeTypeEval)),
      indent('ChangeType = ' + str(self.ChangeType)),
      indent('OutputType = ' + str(self.OutputType)),
      indent('DataClass = ' + str(self.DataClass)),
      indent('IsImplicit = ' + str(self.IsImplicit)),
    '}'))

class ProcessImpulseMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Type = ProcessImpulseType(meta.Type)
    self.Field = ProcessFieldInfo(meta.Field)
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Type = ' + str(self.Type)),
      indent('Field = ' + str(self.Field)),
    '}'))

class ProcessOperationMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Field = ProcessFieldInfo(meta.Field)
    self.IsSelf = meta.IsSelf
    self.IsAsync = meta.IsAsync
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Field = ' + str(self.Field)),
      indent('IsSelf = ' + str(self.IsSelf)),
      indent('IsAsync = ' + str(self.IsAsync)),
    '}'))

class ProcessReferenceMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.ReferenceType = ProcessType(meta.ReferenceType)
    self.Field = ProcessFieldInfo(meta.Field)
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('ReferenceType = ' + str(self.ReferenceType)),
      indent('Field = ' + str(self.Field)),
    '}'))

class ProcessGlobalRefMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.ValueType = ProcessType(meta.ValueType)
    self.Field = ProcessFieldInfo(meta.Field)
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('ValueType = ' + str(self.ValueType)),
      indent('Field = ' + str(self.Field)),
    '}'))

class ProcessInputListMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Field = ProcessFieldInfo(meta.Field)
    self.DefaultValue = meta.DefaultValue
    self.IsConditional = meta.IsConditional
    self.IsListeningToChanges = meta.IsListeningToChanges
    self.IsListeningToChangesEval = ProcessPropertyInfo(meta.IsListeningToChangesEval)
    self.CrossRuntime = ProcessCrossRuntimeInputAttribute(meta.CrossRuntime)
    self.IsPotentiallyListeningToChanges = meta.IsPotentiallyListeningToChanges
    self.TypeConstraint = ProcessType(meta.TypeConstraint)
    self.DataClassConstraint = ProcessDataClass(meta.DataClassConstraint)
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Field = ' + str(self.Field)),
      indent('DefaultValue = ' + str(self.DefaultValue)),
      indent('IsConditional = ' + str(self.IsConditional)),
      indent('IsListeningToChanges = ' + str(self.IsListeningToChanges)),
      indent('IsListeningToChangesEval = ' + str(self.IsListeningToChangesEval)),
      indent('CrossRuntime = ' + str(self.CrossRuntime)),
      indent('IsPotentiallyListeningToChanges = ' + str(self.IsPotentiallyListeningToChanges)),
      indent('TypeConstraint = ' + str(self.TypeConstraint)),
      indent('DataClassConstraint = ' + str(self.DataClassConstraint)),
    '}'))

class ProcessOutputListMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Field = ProcessFieldInfo(meta.Field)
    self.ChangeTypeEval = ProcessPropertyInfo(meta.ChangeTypeEval)
    self.ChangeType = ProcessOutputChangeSource(meta.ChangeType)
    self.TypeConstraint = ProcessType(meta.TypeConstraint)
    self.DataClassConstraint = ProcessDataClass(meta.DataClassConstraint)
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Field = ' + str(self.Field)),
      indent('ChangeTypeEval = ' + str(self.ChangeTypeEval)),
      indent('ChangeType = ' + str(self.ChangeType)),
      indent('TypeConstraint = ' + str(self.TypeConstraint)),
      indent('DataClassConstraint = ' + str(self.DataClassConstraint)),
    '}'))

class ProcessImpulseListMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Type = ProcessImpulseType(meta.Type)
    self.Field = ProcessFieldInfo(meta.Field)
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Type = ' + str(self.Type)),
      indent('Field = ' + str(self.Field)),
    '}'))

class ProcessOperationListMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Field = ProcessFieldInfo(meta.Field)
    self.SupportsSync = meta.SupportsSync
    self.SupportsAsync = meta.SupportsAsync
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Field = ' + str(self.Field)),
      indent('SupportsSync = ' + str(self.SupportsSync)),
      indent('SupportsAsync = ' + str(self.SupportsAsync)),
    '}'))

class ProcessGlobalRefListMetadata:
  def __init__(self, meta):
    self.Index = meta.Index
    self.Name = meta.Name
    self.Field = ProcessFieldInfo(meta.Field)
  
  def __str__(self):
    return '\n'.join((' {',
      indent('Index = ' + str(self.Index)),
      indent('Name = ' + str(self.Name)),
      indent('Field = ' + str(self.Field)),
    '}'))

def ProcessDataClass(c):
  return ['Value', 'Object'][c] if c else None

def ProcessType(t):
  return t # idk

def ProcessFieldInfo(f):
  return f # idk

def ProcessPropertyInfo(p):
  return p # idk

def ProcessCrossRuntimeInputAttribute(a):
  return a # idk

def ProcessOutputChangeSource(s):
  return ['Passthrough', 'Individual', 'Continuous', 'Dynamic'][s]

def ProcessImpulseType(s):
  return ['Continuation', 'Call', 'AsyncCall', 'SyncResumption', 'AsyncResumption'][s]