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
        name = tuple(m[0].lower().split())
        yield Token(IDENT, name, bounds)
        continue
      assert False, 'no match ): ' + repr(s.s[:20])

if __name__ == '__main__':
  with open('l.pft') as f:
    s = f.read()
  for token in lex(s):
    print(token)