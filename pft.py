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
  def __init__(self, kind = None, value = None):
    self.kind = kind
    self.value = value
  
  def set(self, kind, value):
    self.kind = kind
    self.value = value
  
  def __repr__(self):
    return f'Token({repr(self.kind)}, {repr(self.value)})'

class TokenString:
  # a string with some methods to make tokens
  def __init__(self, s):
    self.original = s
    self.s = s
  
  def maketoken(self, split):
    start = len(self.original) - len(self.s)
    end = start + split
    token = Token()
    token.start = start
    token.end = end
    self.s = self.s[split:]
    return token

  def stripcomments(self):
    while self.s.strip().startswith('/'):
      self.s = self.s.strip()
      if self.s[1] == '/':
        _,self.s = self.s.split('\n', maxsplit = 1)
      elif self.s[1] == '*':
        _,self.s = self.s.split('*/', maxsplit = 1)
      else:
        break
    self.s = self.s.strip()
    return self.s
  
  def startswith(self, s):
    return self.s.startswith(s)

# first a lexer
# converts a string into tokens
# <name> <number> <string>
# ',' '=' '@' ':' '(' ')' '[' ']' '{' '}' '<' '>' '[[' ']]'
def lexone(s):
  s.stripcomments()
  tokens = [
    ',', '=', '@', ':',
    '(', ')',
    '[[', ']]',
    '[', ']',
    '{', '}',
    '<', '>',
  ]
  for littoken in tokens:
    if s.startswith(littoken):
      token = s.maketoken(len(littoken))
      token.set(littoken, littoken)
      return token, s
  if s.s[0] in '0123456789.-+':
    numberregex = '[+-]?[0-9]*\\.?[0-9]*'
    m = re.match(numberregex, s.s)
    if m is not None:
      n = m[0]
      token = s.maketoken(len(n))
      if n in ['+', '-']:
        token.set('int', 0) # "special case"
      elif n == ['+.', '-.', '.']:
        token.set('float', 0.) # "special case"
      elif '.' in n:
        token.set('float', float(n))
      else:
        token.set('int', int(n))
      return token, s
  if s.s[0] == '"': # take that you only get double quoted strings
    stringregex = '"([^"\\\\]|\\\\"|\\\\\\\\)*"' # if you want special characters, you get them yourself
    m = re.match(stringregex, s.s)
    if m is not None:
      ss = m[0]
      token = s.maketoken(len(ss))
      ss = ss[1:-1]
      ss = re.sub('\\\\(.)', '\\1', ss)
      token.set('string', ss)
      return token, s
  nameregex = '[/a-zA-Z_][/a-zA-Z_0-9]*(\s+[/a-zA-Z_][/a-zA-Z_0-9]*)*'
  m = re.match(nameregex, s.s)
  if m is not None:
    n = m[0]
    token = s.maketoken(len(n))
    n = tuple(n.split())
    token.set('name', n)
    return token, s
  assert False, 'no match ): ' + repr(s[:20])

def lex(s):
  s = TokenString(s)
  tokens = []
  while s.stripcomments() != '':
    token,s = lexone(s)
    yield token

def pass1(tokens):
  # process @, [ ], [[ ]], < >
  out = []
  tokens = iter(tokens)
  for token in tokens:
    if token.kind == '@':
      token = next(tokens)
      assert token.kind == 'name', f'error: @ before non name: {token}'
      token.kind = 'iname'
    elif token.kind == '[':
      token = next(tokens)
      if token.kind == 'name':
        close = next(tokens)
        assert close.kind == ']', f'error: no matching ]: {close}'
        token.kind = 'fname'
      elif token.kind in ['int', 'float']:
        components = [token]
        while True:
          token = next(tokens)
          if token.kind == ']':
            break
          assert token.kind == ',', f'error: expected comma after components: {components}'
          token = next(tokens)
          assert token.kind in ['int', 'float'], f'error: disallowed component type: {token}'
          components.append(token)
        if 'float' in [token.kind for token in components]:
          ctype = 'float'
        else:
          ctype = 'int'
        assert len(components) in [2, 3, 4], f'error: array of disallowed length: {components}'
        ctype += str(len(components))
        token = Token('literal', (ctype, tuple(token.value for token in components)))
      else:
        assert False, f'error: [ before non name or number: {token}'
    elif token.kind == ']':
      assert False, 'error: unmatched ]'
    elif token.kind == '[[':
      token = next(tokens)
      assert token.kind == 'name', f'error: [[ before non name: {token}'
      close = next(tokens)
      assert close.kind == ']]', f'error: no matching ]]: {close}'
      token.kind = 'rname'
    elif token.kind == ']]':
      assert False, 'error: unmatched ]]'
    elif token.kind == '<':
      token = next(tokens)
      assert token.kind in ['name', 'int', 'float', 'string'], f'error: < before non name: {token}'
      close = next(tokens)
      assert close.kind == '>', f'error: no matching >: {close}'
      token = Token('tag', token)
    elif token.kind == '>':
      assert False, 'error: unmatched >'
    if token.kind in ['float', 'int', 'string']:
      token = Token('literal', (token.kind, token.value))
    if token.kind == 'rname':
      token = Token('literal', [token.kind, token.value])
    out.append(token)
  return out

def pass2(tokens):
  # process ( ), =
  out = []
  tokens = iter(tokens)
  for token in tokens:
    if token.kind == '(':
      token = next(tokens)
      if token.kind == ')':
        token = Token('args', ())
      else:
        assert token.kind in ['name', 'iname', 'fname', 'literal'], f'error: disallowed arg type: {token}'
        args = [token]
        while True:
          token = next(tokens)
          if token.kind == ')':
            break
          assert token.kind == ',', f'error: expected comma after args: {args}'
          token = next(tokens)
          assert token.kind in ['name', 'iname', 'fname', 'literal'], f'error: disallowed arg type: {token}'
          args.append(token)
        token = Token('args', tuple(args))
    elif token.kind == '=':
      token = out.pop()
      assert token.kind in ['name', 'iname'], f'error: non name before =: {token}'
      names = [token]
      while len(out) > 0 and out[-1].kind == ',':
        out.pop()
        token = out.pop()
        assert token.kind in ['name', 'iname'], f'error: non name before , and =: {token}'
        assert token not in names, f'error: duplicate variable: {token}'
        names.insert(0, token)
      token = Token('assign', tuple(names))
    elif token.kind == ')':
      assert False, 'error: unmatched )'
    out.append(token)
  return out

def pass3(tokens):
  # combine <assign>? <fname> <tag>? <args>
  out = []
  for token in tokens:
    if token.kind == 'args':
      args = token.value
      if len(out) > 0 and out[-1].kind == 'tag':
        token = out.pop()
        tag = token.value
      else:
        tag = None
      token = out.pop()
      assert token.kind in ['name', 'fname'], f'error: non name before =: {token}'
      func = token
      if len(out) > 0 and out[-1].kind == 'assign':
        token = out.pop()
        vars_ = token.value
      else:
        vars_ = ()
      token = Token('stmt', (vars_, func, tag, args, []))
    out.append(token)
  return out

def pass4(tokens):
  # combine <any> ':' '{'
  out = []
  for token in tokens:
    if token.kind == '{':
      token = out.pop()
      if token.kind == ':':
        token = out.pop()
        token = Token('subblock', [token])
      else:
        token = Token('block', [token])
    elif token.kind == '}':
      block = []
      while len(out) > 0 and out[-1].kind not in ['block', 'subblock']:
        token = out.pop()
        block.insert(0, token)
      token = out.pop()
      token.value.append(block)
      if token.kind == 'subblock' and len(out) > 0 and out[-1].kind == 'stmt':
        token2 = out.pop()
        token2.value[4].append(token)
        token = token2
    out.append(token)
  return out

def filter2(f, l):
  # split a list into 2 lists
  # the first one when the predicate is true
  # and the second one when the predicate is false
  l1 = []
  l2 = []
  for x in l:
    if f(x):
      l1.append(x)
    else:
      l2.append(x)
  return l1, l2

def reformatstmt(stmt):
  # reformat the statement
  # the order of the parts is the same as in source code
  # reordered to name tag args returns
  # with args and returns split into impulses and not impulses
  #print(stmt)
  assert stmt.kind == 'stmt'
  rets,name,tag,args,subblocks = stmt.value
  argsi,argsv = filter2(lambda arg: arg.kind == 'iname', args)
  retsi,retsv = filter2(lambda ret: ret.kind == 'iname', rets) # returns are (i hope) always variables
  argsi = [[token.kind, token.value] for token in argsi]
  argsv = [[token.kind, token.value] for token in argsv]
  retsi = [[token.kind, token.value] for token in retsi]
  retsv = [[token.kind, token.value] for token in retsv]
  name = [name.kind, name.value]
  if tag is not None:
    tag = [tag.kind, tag.value]
  newsubblocks = []
  for token in subblocks:
    subname,subblock = token.value
    subname = [subname.kind, subname.value]
    newsubblocks.append([subname, [reformatstmt(s) for s in subblock]])
  return [name, tag, argsi, argsv, retsi, retsv, newsubblocks]

def parse(s):
  tokens = lex(s)
  tokens2 = pass1(tokens)
  tokens3 = pass2(tokens2)
  tokens4 = pass3(tokens3)
  tokens5 = pass4(tokens4)
  
  out = [reformatstmt(s) for s in tokens5]
  
  #import pprint
  #pprint.pprint(out)

  return out

#n = ''.join(n).lower()