import re

GATEWAY_PAT = '^gateway (\w+) (\w+)'

DEFINED_GATEWAYS = []

GATEWAYS_SETTINGS = dict()

with open('lang.txt', 'r') as source_code:
    lines = source_code.readlines()
for i in range(len(lines)):
    if lines[i][:-1].startswith('#'):
        pass
    elif re.match(GATEWAY_PAT, lines[i][:-1]):
        print(lines[i][:-1])
        gateway = lines[i][:-1].split()[1]
        DEFINED_GATEWAYS.append(gateway)
        GATEWAYS_SETTINGS [gateway] = {
                'dtype': lines[i][:-1].split()[-1],
                'row_index_declaration': i
            }
print(GATEWAYS_SETTINGS)