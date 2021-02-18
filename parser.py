import re
import pandas as pd

STATE_PAT = '^state (\w+)'
START_PAT = '(\(\s*start\s*=\s*True\s*\))'
TRAP_PAT = '(\(\s*trap\s*=\s*True\s*\))'
TRANSITION_PAT = '(\w*\s+\-\>\s+\w*\s+\:\s+\w*)'

DEFINED_STATES = set()
PHOBOS = None
DEIMOS = dict()
ACTIONS = set()
TEMP_TRANSITIONS = dict()
STATES_SETTINGS = dict()

with open('lang.txt', 'r') as source_code:
    lines = source_code.readlines()
for i in range(len(lines)):
    if lines[i][:-1].startswith('#'):
        pass
    elif re.match(STATE_PAT, lines[i][:-1]):
        state = lines[i][:-1].split()[1]
        DEFINED_STATES.add(state)
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
    elif re.match(TRANSITION_PAT, lines[i][:-1]):
        temp_split = lines[i][:-1].split(':')
        TEMP_TRANSITIONS[temp_split[0]] = temp_split[1].strip()
        ACTIONS.add(temp_split[1].strip())

row_num = len(DEFINED_STATES)
col_num = len(ACTIONS)

ACTIONS, DEFINED_STATES = tuple(ACTIONS), tuple(DEFINED_STATES)

PHOBOS = [[None for i in range(col_num)] for j in range(row_num)]
actions_to_index = {action : i for i, action in enumerate(ACTIONS)}
states_to_index = {state : i for i, state in enumerate(DEFINED_STATES)}

for transition in TEMP_TRANSITIONS:
    PHOBOS[
        states_to_index[transition.split('->')[0].strip()]
    ][
        actions_to_index[TEMP_TRANSITIONS[transition]]
    ] = transition.split('->')[1].strip()

for i in range(len(PHOBOS)):
    for j in range(len(PHOBOS[i])):
        if PHOBOS[i][j] is None:
            PHOBOS[i][j] = DEFINED_STATES[i]


def pretty_matrix():
    global PHOBOS
    print(pd.DataFrame(PHOBOS, columns=ACTIONS, index=DEFINED_STATES))

pretty_matrix()

for i in range(len(PHOBOS)):
    for j in range(len(PHOBOS[i])):
        DEIMOS[tuple([
            DEFINED_STATES[i], ACTIONS[j]
        ])] = PHOBOS[i][j]

import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(DEIMOS)

start_state_present = False
for state in STATES_SETTINGS:
    if STATES_SETTINGS[state]['start']:
        start_state_present = True

class StartStateNotDefined(BaseException):
    pass

if not start_state_present:
    raise StartStateNotDefined('Error1 : Start state is not defined.')


FSM = FSMFactory('setting.txt')

fsm1 = FSM()
