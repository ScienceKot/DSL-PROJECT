import re

string = 'stat S1'

decimal_pat = '^state (\w+)'

print(bool(re.match(decimal_pat, string)))