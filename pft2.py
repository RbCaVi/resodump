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

# not sure what to call this
# wraps a deque or another TokenRange
# and saves all tokens popped through this one
# so i can get better error messages <3
class TokenRange:
  def __init__(self, source):
    self.source = source
    self.tokens = []
  
  def popleft(self):
    token = self.source.popleft()
    self.tokens.append(token)
    return token
  
  def __getitem__(self, i):
    return self.source[i]
  
  def __len__(self):
    return len(self.source)

def assertkind(token, kinds, message):
  if token.kind not in kinds:
    raise PftParseError(token, message)

# hierarchy
# stmts = stmt*
#   stmt = assign? func block*
#    assign = value (',' lvalue)*
#      lvalue = '@' ident | ident
#    func = funcname tag? '(' args ')'
#      funcname = ident | '[' ident ']'
#      tag = '<' ident '>'
#      args = rvalue (',' rvalue)*
#        rvalue = literal | ident | '@' ident
#          literal = int | float | string
#    block = (ident | int) ':' '{' stmts '}'

VAR = 'VAR'
REF = 'REF'
INTARRAY = 'INTARRAY'
FLOATARRAY = 'FLOATARRAY'

def parsestmts(tokens):
  # literally just parse multiple statements in a row
  # so i don't need to save a list of tokens
  stmts = []
  while len(tokens) > 0 and tokens[0].kind != '}': # check for eof and end of block
    stmts.append(ParseStmt(tokens))
  return stmts

class ParseStmt:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    self.assign = ParseAssign(tokens)
    self.func = ParseFunc(tokens)
    self.blocks = parsesubblocks(tokens)
    self.tokens = tokens.tokens

class ParseAssign:
  def __init__(self, tokens):
    self.iout = []
    self.vout = []
    self.tokens = []
    assert len(tokens) >= 2 # needs a variable name and an equals sign
    # check if this actually has either an impulse output (tokens[0] == '@') or an equals (tokens[1] == '=') or a comma (tokens[1] == ',')
    # or check for tokens[1] != '(' and != '<'
    # because otherwise it's a function without assigned variables
    if not (tokens[0].kind == '@' or tokens[1].kind == ',' or tokens[1].kind == '='): # update if `lvalue` changes
      return # this statement does not (explicitly) return any values (it may implicitly return an impulse and/or ignored values)
    if tokens[1].kind in ['(', '<']: # the second token marks it as part of a function # update if `func` changes
      return # this statement does not (explicitly) return any values (it may implicitly return an impulse and/or ignored values)
    tokens = TokenRange(tokens)
    while True:
      if tokens[0].kind == '@':
        self.iout.append(ParseLImpulse(tokens))
      else:
        self.vout.append(ParseLVar(tokens))
      # should i make commas optional? nah
      if (delim := tokens.popleft()).kind == '=':
        break
      assertkind(delim, [','], 'Expected \',\' or \'=\'')
    self.tokens = tokens.tokens

class ParseLImpulse:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    assertkind(tokens.popleft(), ['@'], 'what') # checked by ParseAssign
    assertkind(name := tokens.popleft(), [IDENT], 'Expected IDENT (impulse name)')
    self.name = name
    self.tokens = tokens.tokens

class ParseLVar:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    assertkind(name := tokens.popleft(), [IDENT], 'Expected IDENT (impulse name)')
    self.name = name
    self.tokens = tokens.tokens

class ParseFunc:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    self.name = ParseFuncName(tokens)
    if tokens[0].kind == '<':
      self.tag = ParseTag(tokens)
    else:
      self.tag = None
    assertkind(tokens.popleft(), ['('], 'Expected \'(\' (begin argument list) or \'<\' (begin tag)')
    self.iin = []
    self.vin = []
    if tokens[0].kind == ')': # empty arguments
      tokens.popleft()
    else:
      while True:
        if tokens[0].kind == '@':
          self.iin.append(ParseRImpulse(tokens))
        else:
          self.vin.append(ParseRValue(tokens))
        # should i make commas optional? nah
        if (delim := tokens.popleft()).kind == ')':
          break
        assertkind(delim, [','], 'Expected \',\' or \')\' (end argument list)')
        if tokens[0].kind == ')': # allow trailing comma in argument list <3
          tokens.popleft()
          break
    self.tokens = tokens.tokens

class ParseFuncName:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    if tokens[0].kind == '[':
      assertkind(tokens.popleft(), ['['], 'what') # checked
      assertkind(name := tokens.popleft(), IDENT, 'Expected IDENT (user defined function name)')
      self.name = name
      self.builtin = False
      assertkind(tokens.popleft(), [']'], 'Expected \']\' (end user defined function name)')
    else:
      assertkind(name := tokens.popleft(), IDENT, 'Expected IDENT (builtin function name) or \'[\' (begin user defined function name)')
      self.name = name
      self.builtin = True
    self.tokens = tokens.tokens

class ParseTag:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    assertkind(tokens.popleft(), ['<'], 'what') # checked
    assertkind(name := tokens.popleft(), IDENT, 'Expected IDENT (tag)')
    self.name = name
    self.builtin = False
    assertkind(tokens.popleft(), ['>'], 'Expected \'>\' (end tag)')
    self.tokens = tokens.tokens

class ParseRImpulse:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    assertkind(tokens.popleft(), ['@'], 'what') # checked by ParseFunc
    assertkind(name := tokens.popleft(), [IDENT], 'Expected IDENT (impulse name)')
    self.name = name
    self.tokens = tokens.tokens

class ParseRValue:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    assertkind(value := tokens.popleft(), [INT, FLOAT, STRING, IDENT, '[', '[['], 'Expected INT, FLOAT, STRING, IDENT (variable name), \'[\' (begin array), or \'[[\' (begin reference)')
    if value.kind in [INT, FLOAT, STRING]:
      self.value = value.value
      self.kind = value.kind
    elif value.kind == IDENT:
      self.value = value.value
      self.kind = VAR
    if value.kind == '[':
      values = []
      isfloat = False
      while True:
        assertkind(value := tokens.popleft(), [INT, FLOAT], 'Expected INT or FLOAT (array element)')
        isfloat |= value.kind == FLOAT
        values.append(value.value)
        # should i make commas optional? nah
        if (delim := tokens.popleft()).kind == ']':
          break
        assertkind(delim, [','], 'Expected \',\' or \']\' (end array)')
        if tokens[0].kind == ']': # trailing comma is allowed in array literal
          tokens.popleft()
          break
      self.value = values
      self.kind = FLOATARRAY if isfloat else INTARRAY
    if value.kind == '[[':
      assertkind(ref := tokens.popleft(), [IDENT], 'Expected IDENT (reference target)')
      assertkind(tokens.popleft(), [']]'], 'Expected \']]\' (end reference)')
      self.value = ref.value
      self.kind = REF
    self.tokens = tokens.tokens

def parsesubblocks(tokens):
  subblocks = []
  while len(tokens) >= 2 and tokens[1].kind == ':': # check if there's a block marker
    subblocks.append(ParseSubBlock(tokens))
  return subblocks

class ParseSubBlock:
  def __init__(self, tokens):
    tokens = TokenRange(tokens)
    assertkind(label := tokens.popleft(), [INT, IDENT], 'Expected INT or IDENT')
    assertkind(tokens.popleft(), [':'], 'what') # checked in parsesubblocks
    assertkind(tokens.popleft(), ['{'], 'Expected \'{\' (begin subblock)')
    self.label = label.value
    self.stmts = parsestmts(tokens)
    assertkind(tokens.popleft(), ['}'], 'Expected \'}\' (end subblock)')
    self.tokens = tokens.tokens



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