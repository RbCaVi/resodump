import json

import readfrdt

with open('a2b9eaefdc7397c7d87402f5fc3ef5f73969249a39f54d15f4e646721757cf11.brson', 'rb') as f:
  data = f.read()

tree = readfrdt.readfrdt(data)

with open('tree.json', 'w') as f:
  json.dump(tree, f)