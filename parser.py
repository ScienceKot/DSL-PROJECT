import re

STATE_PAT = '^state (\w+)'
START_PAT = '(\(\s*start\s*=\s*True\s*\))'
TRAP_PAT = '(\(\s*trap\s*=\s*True\s*\))'

DEFINED_STATES = []

STATES_SETTINGS = dict()

with open('lang.txt', 'r') as source_code:
    lines = source_code.readlines()
for i in range(len(lines)):
    if lines[i][:-1].startswith('#'):
        pass
    elif re.match(STATE_PAT, lines[i][:-1]):
        state = lines[i][:-1].split()[1]
        DEFINED_STATES.append(state)
        if bool(re.search(START_PAT, state)):
            STATES_SETTINGS[state.replace(re.search(START_PAT, state).group(0), '')] = {
                'start' : True,
                'trap' : False,
                'row_index_declaration' : i
            }
        elif bool(re.search(TRAP_PAT, state)):
            STATES_SETTINGS[state.replace(re.search(TRAP_PAT, state).group(0), '')] = {
                'start': False,
                'trap': True,
                'row_index_declaration': i
            }
        else:
            STATES_SETTINGS[state] = {
                'start' : False,
                'trap' : False,
                'row_index_declaration': i
            }
start_state_present = False
for state in STATES_SETTINGS:
    if STATES_SETTINGS[state]['start']:
        start_state_present = True

class StartStateNotDefined(BaseException):
    pass

if not start_state_present:
    raise StartStateNotDefined('Error1 : Start state is not defined.')

