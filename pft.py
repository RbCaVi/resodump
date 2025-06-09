# protoflux text format ("assembly")

# <code> = <stmt>*
# <stmt> = (<cname> (',' <cname>)* '=') <fname> <args>? <block>*
# <cname> = <name> | '@' <name>
# <fname> = <name> | '[' <name> ']'
# <args> = '(' ')' | '(' <arg> (',' <arg>)* ')'
# <block> = <name> ':' '{' <code> '}'
# <arg> = <cname> | <literal>
# <literal> = <number> | <string> | '[[' <name> ']]'
# <name> = <word>+
# <word> = [a-zA-Z_][a-zA-Z_0-9]*

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
# ',' '=' '@' ':' '(' ')' '[' ']' '{' '}' '[[' ']]'
def lexone(s):
  s = stripcomments(s)
  tokens = [
    ',', '=', '@', ':',
    '(', ')',
    '[[', ']]',
    '[', ']',
    '{', '}',
  ]
  for token in tokens:
    if s.startswith(token):
      s = s[len(token):]
      return token, s
  if s[0] in '0123456789.-+':
    numberregex = '[+-]?[0-9]*(\\.[0-9]*)?'
    m = re.match(numberregex, s)
    if m is not None:
      n = m[0]
      s = s[len(n):]
      if n in ['+', '-']:
        return 0 # special case"
      if n in ['.']:
        return 0. # special case"
      if '.' in n:
        return float(n), s
      else:
        return int(n), s
  if s[0] == '"': # take that you only get double quoted strings
    stringregex = '"([^"\\\\]|\\\\"|\\\\\\\\)*"' # if you want special characters, you get them yourself
    m = re.match(stringregex, s)
    if m is not None:
      ss = m[0]
      s = s[len(ss):]
      ss = ss[1:-1]
      ss = re.sub('\\\\(.)', '\\1', ss)
      return ss, s
  nameregex = '[a-zA-Z_][a-zA-Z_0-9]*(\s+[a-zA-Z_][a-zA-Z_0-9]*)*'
  m = re.match(nameregex, s)
  if m is not None:
    n = m[0]
    s = s[len(n):]
    n = n.split()
    return n, s
  assert False, 'no match ): ' + repr(s[:20])

def lex(s):
  tokens = []
  while stripcomments(s) != '':
    token,s = lexone(s)
    tokens.append(token)
  return tokens

with open('i.pft') as f:
  s = f.read()

tokens = lex(s)