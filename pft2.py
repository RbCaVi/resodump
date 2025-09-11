# protoflux text format ("assembly")

# <code> = <stmt>*
# <stmt> = (<iname> (',' <iname>)* '=') <fname> <args> <block>*
# <iname> = <name> | '@' <name>
# <fname> = <name> <tag>? | '[' <name> ']'
# <tag> = '<' <name> '>'
# <args> = '(' ')' | '(' <arg> (',' <arg>)* ')'
# <block> = <name> ':' '{' <code> '}'
# <arg> = <iname> | <literal>
# <literal> = <number> | <string> | '[' <number> (',' <number>*) ']' | '[[' <name> ']]'
# <name> = <word>+
# <word> = [/a-zA-Z_][/a-zA-Z_0-9]*

import re
import collections

class PftError(Exception):
  pass

class PftParseError(PftError):
  def __init__(self, token, message):
    self.source = token.source
    self.start = token.start
    self.end = token.end
    self.message = message

class PftLexError(PftError):
  def __init__(self, source, message):
    self.source = source
    self.start = self.source.consumed()
    self.end = self.start + 1
    self.message = message

class Token:
  def __init__(self, kind, value, bounds):
    self.kind = kind
    self.value = value
    self.source,self.start,self.end = bounds
  
  def __repr__(self):
    return f'Token({repr(self.kind)}, {repr(self.value)})'

class TokenString:
  # a string with some methods to make tokens
  def __init__(self, s):
    self.original = s
    self.s = s
  
  def matchstr(self, s):
    if not self.s.startswith(s):
      return None, None
    l = len(s)
    start = len(self.original) - len(self.s)
    end = start + l
    self.s = self.s[l:]
    return s, (self, start, end)
  
  def match(self, pattern):
    m = re.match(pattern, self.s)
    if m is None:
      return None, None
    l = len(m[0])
    start = len(self.original) - len(self.s)
    end = start + l
    self.s = self.s[l:]
    return m, (self, start, end)

  def strip(self):
    # strips spaces and single line // and multi line /* */ comments
    while True:
      self.s = self.s.strip()
      if not self.s.strip().startswith('/'):
        return
      if self.s[1] == '/':
        _,self.s = self.s.split('\n', maxsplit = 1)
      elif self.s[1] == '*':
        _,self.s = self.s.split('*/', maxsplit = 1)
      else:
        break
  
  def startswith(self, s):
    return self.s.startswith(s)
  
  def __len__(self):
    return len(self.s)
  
  def consumed(self):
    return len(self.original) - len(self.s)

# first a lexer
# converts a string into tokens
# <name> <number> <string>
# ',' '=' '@' ':' '(' ')' '[' ']' '{' '}' '<' '>' '[[' ']]'
littokens = [
  ',', '=', '@', ':',
  '(', ')',
  '[[', ']]',
  '[', ']',
  '{', '}',
  '<', '>',
]

INT = 'INT'
FLOAT = 'FLOAT'
STRING = 'STRING'
IDENT = 'IDENT'
VAR = 'VAR'
REF = 'REF'
ARRAY = 'ARRAY'

numberregex = '[+-]?[0-9]*\\.?[0-9]*'
stringregex = '"([^"\\\\]|\\\\"|\\\\\\\\)*"' # if you want special characters, you get them yourself # take that you only get double quoted strings
nameregex = '[/a-zA-Z_][/a-zA-Z_0-9]*(\s+[/a-zA-Z_][/a-zA-Z_0-9]*)*'

def lex(s):
  s = TokenString(s)
  while True:
    s.strip()
    if len(s) == 0:
      return
    for littoken in littokens:
      m,bounds = s.matchstr(littoken)
      if m is not None:
        yield Token(m, m, bounds)
        break
    else:
      m,bounds = s.match(numberregex)
      if m is not None and len(m[0]) != 0:
        num = m[0]
        if num in ['+', '-']:
          yield Token(INT, 0, bounds) # "special case"
        elif num in ['+.', '-.', '.']:
          yield Token(FLOAT, 0., bounds) # "special case"
        elif '.' in num:
          yield Token(FLOAT, num, bounds)
        else:
          yield Token(INT, num, bounds)
        continue
      m,bounds = s.match(stringregex)
      if m is not None:
        string = re.sub('\\\\(.)', '\\1', m[0][1:-1])
        yield Token(STRING, string, bounds)
        continue
      m,bounds = s.match(nameregex)
      if m is not None:
        name = tuple(m[0].split())
        yield Token(IDENT, name, bounds)
        continue
      raise PftLexError(s, 'No matching token here')

# tokens is a deque for all of these
# i could have used some kind of peekable iterator
# but nah i'd win
# i could also write a reversed list class that pops from the start without O(n) time complexity

class Stmt:
  def __init__(self, func, iin, vin, iout, vout, subblocks):
    self.func = func
    self.iin = iin
    self.vin = vin
    self.iout = iout
    self.vout = vout
    self.subblocks = subblocks

class FuncName:
  def __init__(self, name, builtin):
    self.token = name
    self.name = name.value
    self.builtin = builtin

class Value:
  def __init__(self, value, kind):
    self.value = value
    self.kind = kind

def assertkind(token, kinds, message):
  if token.kind not in kinds:
    raise PftParseError(token, message)

def parsestmts(tokens):
  stmts = []
  while len(tokens) > 0 and tokens[0].kind != '}':
    stmts.append(parsestmt(tokens))
  return stmts

def parsestmt(tokens):
  iout,vout = parseassign(tokens)
  func,iin,vin = parsefunc(tokens)
  subblocks = parsesubblocks(tokens)
  return Stmt(func, iin, vin, iout, vout, subblocks)

def parseassign(tokens):
  assert len(tokens) >= 2 # needs a variable name and an equals sign
  # check if this actually has either an impulse output (tokens[0] == '@') or an equals (tokens[1] == '=') or a comma (tokens[1] == ',')
  # or check for tokens[1] != '(' and != '<'
  # because otherwise it's a function without assigned variables
  if not (tokens[0].kind == '@' or tokens[1].kind == ',' or tokens[1].kind == '='):
    return [], [] # this statement does not (explicitly) return any values
  if tokens[1].kind in ['(', '<']: # the second token marks it as part of a function
    return [], [] # this statement does not (explicitly) return any values
  iout = []
  vout = []
  while True:
    if (var := tokens.popleft()).kind == '@':
      vlist = iout
      var = tokens.popleft()
    else:
      vlist = vout
    assertkind(var, [IDENT], 'Expected IDENT (assigned variable)')
    vlist.append(var)
    # should i make commas optional? nah
    if (delim := tokens.popleft()).kind == '=':
      break
    assertkind(delim, [','], 'Expected \',\' or \'=\'')
  return iout, vout

def parsefunc(tokens):
  name = parsefuncname(tokens)
  if (left := tokens.popleft()).kind == '<': # you only need one token in a tag right?
    assertkind(tag := tokens.popleft(), [INT, IDENT], 'Expected INT or IDENT')
    assertkind(tokens.popleft(), ['>'], 'Expected \'>\' (end tag)')
    left = tokens.popleft()
  else:
    tag = None
  func = name, tag
  assertkind(left, ['('], 'Expected \'(\' (begin argument list) or \'<\' (begin tag)')
  iin = []
  vin = []
  if tokens[0].kind == ')': # empty arguments
    tokens.popleft()
    return func, [], []
  while True:
    if tokens[0].kind == '@':
      tokens.popleft()
      assertkind(var := tokens.popleft(), [IDENT], 'Expected IDENT (impulse input name)')
      iin.append(var)
    else:
      vin.append(parsevalue(tokens))
    # should i make commas optional? nah
    if (delim := tokens.popleft()).kind == ')':
      break
    assertkind(delim, [','], 'Expected \',\' or \')\' (end argument list)')
    if tokens[0].kind == ')':
      tokens.popleft()
      break
  return func, iin, vin

def parsefuncname(tokens):
  if (name := tokens.popleft()).kind == '[':
    name = tokens.popleft()
    assertkind(name, IDENT, 'Expected IDENT (user defined function name)')
    assertkind(tokens.popleft(), [']'], 'Expected \']\' (end user defined function name)')
    return FuncName(name, False)
  else:
    assertkind(name, IDENT, 'Expected IDENT (builtin function name)')
    return FuncName(name, True)

def parsevalue(tokens):
  assertkind(value := tokens.popleft(), [INT, FLOAT, STRING, IDENT, '[', '[['], 'Expected INT, FLOAT, STRING, IDENT (variable name), \'[\' (begin array), or \'[[\' (begin reference)')
  if value.kind in [INT, FLOAT, STRING]:
    return Value(value, value.kind)
  if value.kind == IDENT:
    return Value(value, VAR)
  if value.kind == '[':
    values = []
    while True:
      assertkind(value := tokens.popleft(), [INT, FLOAT], 'Expected INT or FLOAT')
      values.append(value)
      # should i make commas optional? nah
      if (delim := tokens.popleft()).kind == ']':
        break
      assertkind(delim, [','], 'Expected \',\' or \']\' (end array)')
      if tokens[0].kind == ']':
        tokens.popleft()
        break
    return Value(values, ARRAY)
  if value.kind == '[[':
    ref = tokens.popleft()
    assertkind(tokens.popleft(), [']]'], 'Expected \']]\' (end reference)')
    return Value(ref, REF)

def parsesubblocks(tokens):
  subblocks = []
  while len(tokens) >= 2 and tokens[1].kind == ':':
    assertkind(label := tokens.popleft(), [INT, IDENT], 'Expected INT or IDENT')
    assertkind(tokens.popleft(), [':'], 'what') # i know this one is a colon because of the check above
    assertkind(tokens.popleft(), ['{'], 'Expected \'{\' (begin subblock)')
    subblocks.append((label, parsestmts(tokens)))
    assertkind(tokens.popleft(), ['}'], 'Expected \'}\' (end subblock)')
  return subblocks

def dumpstmts(stmts):
  return '\n'.join(dumpstmt(stmt) for stmt in stmts)

def dumpstmt(stmt):
  funcname,tag = stmt.func
  dumped = ' '.join(funcname.name)
  if not funcname.builtin:
    dumped = '[' + dumped + ']'
  outputs = ['@' + ' '.join(i.value) for i in stmt.iout] + [' '.join(v.value) for v in stmt.vout]
  if len(outputs) != 0:
    dumped = ','.join(outputs) + ' = ' + dumped
  if tag is not None:
    dumped += ' <' + ' '.join(tag.value) + '>'
  inputs = ['@' + ' '.join(i.value) for i in stmt.iin] + [dumpvalue(v) for v in stmt.vin]
  dumped += ' (' + ', '.join(inputs) + ')'
  for label,substmts in stmt.subblocks:
    dumped += '\n  ' + ' '.join(label.value) + ': {\n    ' + dumpstmts(substmts).replace('\n', '\n    ') + '\n  }'
  return dumped

def dumpvalue(value):
  if value.kind == VAR:
    return ' '.join(value.value.value)
  if value.kind == REF:
    return '[[' + ' '.join(value.value.value) + ']]'
  if value.kind == FLOAT:
    return str(value.value.value)
  if value.kind == INT:
    return str(value.value.value)
  if value.kind == ARRAY:
    return '[' + ', '.join([str(v.value) for v in value.value]) + ']'
  if value.kind == STRING:
    return '"' + value.value.value.replace('"', '\"').replace('\\', '\\\\') + '"'
  print(value, value.kind)

if __name__ == '__main__':
  with open('l.pft') as f:
    s = f.read()
  tokens = collections.deque()
  for token in lex(s):
    tokens.append(token)
  try:
    print(stmts := parsestmts(tokens))
  except PftParseError:
    print([tokens[i] for i in range(9)])
    raise
  print(dumpstmts(stmts))