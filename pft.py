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

def stripcomments(s):
  while s.strip().startswith('/'):
    s = s.strip()
    if s[1] == '/':
      _,s = s.split('\n', maxsplit = 1)
    elif s[1] == '*':
      _,s = s.split('*/', maxsplit = 1)
    else:
      break
  return s.strip()

# first a lexer
# converts a string into tokens
# <name> <number> <string>
# ',' '=' '@' ':' '(' ')' '[' ']' '{' '}' '<' '>' '[[' ']]'
def lexone(s):
  s = stripcomments(s)
  tokens = [
    ',', '=', '@', ':',
    '(', ')',
    '[[', ']]',
    '[', ']',
    '{', '}',
    '<', '>',
  ]
  for token in tokens:
    if s.startswith(token):
      s = s[len(token):]
      return [token], s
  if s[0] in '0123456789.-+':
    numberregex = '[+-]?[0-9]*\\.?[0-9]*'
    m = re.match(numberregex, s)
    if m is not None:
      n = m[0]
      s = s[len(n):]
      if n in ['+', '-']:
        return ['int', 0], s # special case"
      if n in ['.']:
        return ['float', 0.], s # special case"
      if '.' in n:
        return ['float', float(n)], s
      else:
        return ['int', int(n)], s
  if s[0] == '"': # take that you only get double quoted strings
    stringregex = '"([^"\\\\]|\\\\"|\\\\\\\\)*"' # if you want special characters, you get them yourself
    m = re.match(stringregex, s)
    if m is not None:
      ss = m[0]
      s = s[len(ss):]
      ss = ss[1:-1]
      ss = re.sub('\\\\(.)', '\\1', ss)
      return ['string', ss], s
  nameregex = '[/a-zA-Z_][/a-zA-Z_0-9]*(\s+[/a-zA-Z_][/a-zA-Z_0-9]*)*'
  m = re.match(nameregex, s)
  if m is not None:
    n = m[0]
    s = s[len(n):]
    n = tuple(n.split())
    return ['name', n], s
  assert False, 'no match ): ' + repr(s[:20])

def lex(s):
  tokens = []
  while stripcomments(s) != '':
    token,s = lexone(s)
    tokens.append(token)
  return tokens

def pass1(tokens):
  # process @, [ ], [[ ]], < >, =
  out = []
  while len(tokens) > 0:
    token = tokens.pop(0)
    if token[0] == '@':
      token = tokens.pop(0)
      assert token[0] == 'name', f'error: @ before non name: {token}'
      token[0] = 'iname'
    elif token[0] == '[':
      token = tokens.pop(0)
      if token[0] == 'name':
        close = tokens.pop(0)
        assert close[0] == ']', f'error: no matching ]: {close}'
        token[0] = 'fname'
      elif token[0] in ['int', 'float']:
        components = [token]
        while True:
          token = tokens.pop(0)
          if token[0] == ']':
            break
          assert token[0] == ',', f'error: expected comma after components: {components}'
          token = tokens.pop(0)
          assert token[0] in ['int', 'float'], f'error: disallowed component type: {token}'
          components.append(token)
        if 'float' in [t for t,v in components]:
          ctype = 'float'
        else:
          ctype = 'int'
        assert len(components) in [2, 3, 4], f'error: array of disallowed length: {components}'
        ctype += str(len(components))
        token = ('literal', ctype, tuple(v for t,v in components))
      else:
        assert False, f'error: [ before non name or number: {token}'
    elif token[0] == ']':
      assert False, 'error: unmatched ]'
    elif token[0] == '[[':
      token = tokens.pop(0)
      assert token[0] == 'name', f'error: [[ before non name: {token}'
      close = tokens.pop(0)
      assert close[0] == ']]', f'error: no matching ]]: {close}'
      token[0] = 'rname'
    elif token[0] == ']]':
      assert False, 'error: unmatched ]]'
    elif token[0] == '<':
      token = tokens.pop(0)
      assert token[0] in ['name', 'int', 'float', 'string'], f'error: < before non name: {token}'
      close = tokens.pop(0)
      assert close[0] == '>', f'error: no matching >: {close}'
      token = ('tag', token)
    elif token[0] == '>':
      assert False, 'error: unmatched >'
    elif token[0] == '=':
      token = out.pop()
      assert token[0] in ['name', 'iname'], f'error: non name before =: {token}'
      names = [token]
      while len(out) > 0 and out[-1][0] == ',':
        out.pop()
        token = out.pop()
        assert token[0] in ['name', 'iname'], f'error: non name before , and =: {token}'
        assert token not in names, f'error: duplicate variable: {token}'
        names.insert(0, token)
      token = ('assign', tuple(names))
    if token[0] in ['float', 'int', 'string']:
      token = ('literal', token[0], token[1])
    if token[0] == 'rname':
      token = ['literal', token[0], token[1]]
    out.append(token)
  return out

def pass2(tokens):
  # process ( )
  out = []
  while len(tokens) > 0:
    token = tokens.pop(0)
    if token[0] == '(':
      token = tokens.pop(0)
      if token[0] == ')':
        token = ('args', ())
      else:
        assert token[0] in ['name', 'iname', 'fname', 'literal'], f'error: disallowed arg type: {token}'
        args = [token]
        while True:
          token = tokens.pop(0)
          if token[0] == ')':
            break
          assert token[0] == ',', f'error: expected comma after args: {args}'
          token = tokens.pop(0)
          assert token[0] in ['name', 'iname', 'fname', 'literal'], f'error: disallowed arg type: {token}'
          args.append(token)
        token = ('args', tuple(args))
    elif token[0] == ')':
      assert False, 'error: unmatched )'
    out.append(token)
  return out

def pass3(tokens):
  # combine <assign>? <fname> <tag>? <args>
  out = []
  while len(tokens) > 0:
    token = tokens.pop(0)
    if token[0] == 'args':
      args = token[1]
      if len(out) > 0 and out[-1][0] == 'tag':
        token = out.pop()
        tag = token[1]
      else:
        tag = None
      token = out.pop()
      assert token[0] in ['name', 'fname'], f'error: non name before =: {token}'
      func = token
      if len(out) > 0 and out[-1][0] == 'assign':
        token = out.pop()
        vars_ = token[1]
      else:
        vars_ = ()
      token = ('stmt', vars_, func, tag, args, [])
    out.append(token)
  return out

def pass4(tokens):
  # combine <any> ':' '{'
  out = []
  while len(tokens) > 0:
    token = tokens.pop(0)
    if token[0] == '{':
      token = out.pop()
      if token[0] == ':':
        token = out.pop()
        token = ['subblock', token]
      else:
        token = ['block', token]
    elif token[0] == '}':
      block = []
      while len(out) > 0 and out[-1][0] not in ['block', 'subblock']:
        token = out.pop()
        block.insert(0, token)
      token = out.pop()
      token.append(block)
      if token[0] == 'subblock' and len(out) > 0 and out[-1][0] == 'stmt':
        token2 = out.pop()
        token2[5].append(token)
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
  assert stmt[0] == 'stmt'
  _,rets,name,tag,args,subblocks = stmt
  argsi,argsv = filter2(lambda arg: arg[0] == 'iname', args)
  retsi,retsv = filter2(lambda ret: ret[0] == 'iname', rets) # returns are (i hope) always variables
  newsubblocks = []
  for _,subname,subblock in subblocks:
    newsubblocks.append([subname, [reformatstmt(s) for s in subblock]])
  return [name, tag, argsi, argsv, retsi, retsv, newsubblocks]

def parse(s):
  tokens = lex(s)
  tokens2 = pass1(tokens)
  tokens3 = pass2(tokens2)
  tokens4 = pass3(tokens3)
  tokens5 = pass4(tokens4)
  
  out = [reformatstmt(s) for s in tokens5]

  return out

#n = ''.join(n).lower()