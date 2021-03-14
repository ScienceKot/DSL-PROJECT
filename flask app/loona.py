# Importing all needed libraries.
from collections import OrderedDict
import re
from time import sleep
import pandas as pd

class NoStartStateIsDefinedError(Exception):
    '''
        Raised when a start state isn't defined.
    '''
    pass

class NoSuchGateway(Exception):
    '''
        Raised when a gateway is used without being defined.
    '''
    pass

class StateNotDefined(Exception):
    '''
        Raised when a state is used in a transition without being defined.
    '''
    pass

class WrongDataType(Exception):
    '''
        Raised when a transition functions gets a unexistent data type.
    '''
    pass

class NoSuchTransitionFunction(Exception):
    '''
        Raised when a transition function is used that doesn't exist in the loona language.
    '''
    pass

# The main MetaClass
class LoonaMetaClass(type):
    @classmethod
    def __prepare__(cls, name : str, bases : tuple) -> OrderedDict:
        '''
            Overwriting the __prepare__ magic function.
        :param name: str
            The name of the new created class.
        :param bases: tuple
            The tuple with the classes inherited by the new created class.
        :return: OrderedDict
            The Ordered Dictionary with the arugument : value pairs.
        '''
        return OrderedDict()

    def __change_state(self, action : str) -> None:
        '''
            The function that change the internal state of the FSM.
        :param action: str
            The string form of the action.
        '''
        if action in self.ACTIONS:
            self.start_state = self.DEIMOS[(self.start_state, action)]
        else:
            self.start_state = self.DEIMOS[(self.start_state, '*')]

    def threshold(self, to_compare : str, compare_with : str, rule : str, params : list = None, numeric : bool = False) -> None:
        '''
            The python implementation of the threshold function of the loona DSL.
        :param to_compare: str
            The name of the first argument that should be compared.
        :param compare_with: str
            The name of the second argument that should be compared.
        :param rule: str
            If setted as max then if the first value is bigger than the second one the state is changed.
            If setted as min then if the first value is smaller than the second one the state is changed.
            Else the NoSuchTransitionFunction Error is raised.
        :param params: list
            The list of parameters of the function.
        :param numeric: bool
            If is seted as True then then to the function are passed the values from the gateways.
            Else are passes the name of the gateways.
        '''
        if rule == 'min':

            # If the rule is setted to min the function checks if the first value is smaller than the second one.
            if to_compare < compare_with:
                if numeric:
                    self.__change_state(f'threshold({params[0]}, {int(compare_with)}, {rule})')
                else:
                    self.__change_state(f'threshold({params[0]}, {params[1]}, {rule})')
        elif rule == 'max':

            # If the rule is setted to max the function checks if the first value is bigger than the second one.
            if to_compare > compare_with:
                if numeric:
                    self.__change_state(f'threshold({params[0]}, {int(compare_with)}, {rule})')
                else:
                    self.__change_state(f'threshold({params[0]}, {params[1]}, {rule})')
        else:

            # Else the NoSuchTransitionFunction Error is raised.
            raise NoSuchTransitionFunction(f"No such rule for threshold function -> {rule}")

    def timepassed(self, seconds : int) -> None:
        '''
            The python implementation of the timepassed function of the loona DSL.
        :param seconds: int
            The number of second to wait before the changing the state of the FSM.
        '''
        # Waiting the 'seconds' seconds before changing the state/
        sleep(seconds)
        self.__change_state(f'timepassed({int(seconds)})')

    def equal(self, val1 : str, val2 : str) -> None:
        '''
            The python implementation of the equal function of the loona DSL.
        :param val1: str
            The first value to check if equal to the second one.
        :param val2: str
            The second value to check if equal to the first one.
        '''
        if val1 == val2:
            self.__change_state(f'equal({val1}, {val2})')

    def run(self, kwargs : dict) -> str:
        '''
            The main running function of the FSM, it takes the parameters and changer the state if needed.
        :param kwargs: dict
            The dictionary with the values from the gateways.
        :return: str
            The new state.
        '''
        # Checking if any gateway value passed to FSM have a data type that isn't defined in loona.
        for arg in kwargs:
            if arg in self.GATEWAYS_SETTINGS:
                if type(kwargs[arg]) is self.loonatypes_to_pytypes[self.GATEWAYS_SETTINGS[arg]['dtype']]:
                    pass
                else:
                    raise WrongDataType(f"The dtypes are not matching, wrong type is - {self.GATEWAYS_SETTINGS[arg]['dtype']} \n row - {self.GATEWAYS_SETTINGS[arg]['row_index_declaration']}")

        # Extracting the row of the now active state from PHOBOS.
        row = self.PHOBOS[self.states_to_index[self.start_state]]

        # Checking if the row is full is filled with the same state.
        if row == [self.start_state] * len(row):
            pass
        else:
            # Extracting the indexes from the table row where state is different that the present state/
            different_state_index = [i for i in range(len(row)) if row[i] != self.start_state]

            # Extracting actions for this states.
            actions = [self.index_to_action[index] for index in different_state_index]

            # Iterating throw all the all extracted actions.
            for action in actions:
                # Checking if action is a empty action.
                if '*' in action and self.DEIMOS[(self.start_state, '*')] != self.start_state:
                    self.__change_state('*')
                    return self.start_state
                # Checking if action is equal.
                elif 'equal' in action:
                    # Extracting the parameters from the transition function.
                    params = re.search('(\s*(\w+)\s*\,\s*(\w+)\s*)', action).group(0)
                    params = [param.strip() for param in params.split(',')]

                    # Extracting the numerical values if they exists from the input of gateways.
                    for i in range(len(params)):
                        if params[i] in kwargs:
                            params[i] = kwargs[str(params[i])]

                    # Calling the equal function.
                    self.equal(params[0], params[1])
                    return self.start_state
                # Checking if action is a threshold.
                elif 'threshold' in action:
                    # Extracting the parameters from the transition function.
                    params = re.search('(\s*(\w+)\s*\,\s*(\w+)\s*\,\s*(\w+)\s*)', action).group(0)
                    params = [param.strip() for param in params.split(',')]

                    # Extracting the numerical values if they exists from the input of gateways.
                    for param in params[:-1]:
                        if not param.isnumeric():
                            if param not in self.GATEWAYS_SETTINGS:
                                raise NoSuchGateway(f'No such gateway as {param}')

                    # Calling the threshold with different parameters.
                    if params[1].isnumeric():
                        self.threshold(float(kwargs[params[0]]), float(params[1]), params[2], params, numeric=True)
                    else:
                        self.threshold(float(kwargs[params[0]]), float(kwargs[params[1]]), params[2], params)
                    return self.start_state
                # Checking if action is a timepassed.
                elif 'timepassed' in action:
                    # Extracting the parameters from the transition function.
                    seconds = re.search('(\s*(\d+)\s*)', action).group(0)

                    # Calling the timepassed function.
                    self.timepassed(float(seconds))
                    return self.start_state
                else:
                    # If transition function is defined as one that daesn't exist in loona a NoSuchTransitionFunction
                    # Error is raised.
                    raise NoSuchTransitionFunction(f"{action} doesn't contain any transition function")

    def __init__(cls, file_path : str, bases : tuple):
        '''
            The constructor of the MetaClass.
        :param file_path: str
            The file path to the file with the Loona code.
        :param bases: tuple
            The tuple with the bases classes of the class.
        '''

        super().__init__(file_path, bases, dict())
        # Creatting an empty list of field names.
        cls._field_names = []

        # Defining the mapping of the loona to python data types.
        cls.loonatypes_to_pytypes = {
            'numerical' : float,
            'str' : str,
            'bool' : bool
        }

        # Defining the patterns
        cls.STATE_PAT = '^state (\w+)'
        cls.START_PAT = '(\(\s*start\s*\=\s*True\s*\))'
        cls.TRAP_PAT = '(\(\s*trap\s*\=\s*True\s*\))'
        cls.TRANSITION_PAT = '(\w*\s+\-\>\s+\w*\s+\:\s+\w*)'
        cls.GATEWAY_PAT = '^gateway (\w+) (\w+)'

        # Defining the global variables.
        cls.DEFINED_STATES = set()
        cls.DEFINED_GATEWAYS = set()
        cls.PHOBOS = None
        cls.DEIMOS = dict()
        cls.ACTIONS = set()
        cls.TEMP_TRANSITIONS = dict()
        cls.STATES_SETTINGS = dict()
        cls.GATEWAYS_SETTINGS = dict()

        # Readding the loona code from the source code.
        try:
            with open(file_path, 'r') as source_code:
                lines = source_code.readlines()
        except FileNotFoundError:
            print("Such path doesn't exist")

        # Iterating throw all the lines if the code source.
        for i in range(len(lines)):

            # Skipping the line starting with '#'
            if lines[i][:-1].startswith('#'):
                pass

            # Checking is the row have the pattern state.
            elif re.match(cls.STATE_PAT, lines[i][:-1]):
                state = lines[i][:-1].split()[1]

                # Checking is the declared state is a start state.
                if bool(re.search(cls.START_PAT, state)):
                    cls.STATES_SETTINGS[state.replace(re.search(cls.START_PAT, state).group(0), '')] = {
                        'start': True,
                        'trap': False,
                        'row_index_declaration': i
                    }
                    cls.DEFINED_STATES.add(state.replace(re.search(cls.START_PAT, state).group(0), ''))
                # Checking is the declared state is a trap state.
                elif bool(re.search(cls.TRAP_PAT, state)):
                    cls.STATES_SETTINGS[state.replace(re.search(cls.TRAP_PAT, state).group(0), '')] = {
                        'start': False,
                        'trap': True,
                        'row_index_declaration': i
                    }
                    cls.DEFINED_STATES.add(state.replace(re.search(cls.TRAP_PAT, state).group(0), ''))
                # Setting the state as a normal state.
                else:
                    cls.STATES_SETTINGS[state] = {
                        'start': False,
                        'trap': False,
                        'row_index_declaration': i
                    }
                    cls.DEFINED_STATES.add(state)

            # Checking if in the line is defined as a transition.
            elif re.match(cls.TRANSITION_PAT, lines[i][:-1]):
                temp_split = lines[i][:-1].split(':')

                # Storing the trasition and the action.
                cls.TEMP_TRANSITIONS[temp_split[0].strip()] = temp_split[1].strip()
                cls.ACTIONS.add(temp_split[1].strip())

            # Checking if in the line is defined as a gateway.
            elif re.match(cls.GATEWAY_PAT, lines[i][:-1]):
                gateway = lines[i][:-1].split()[1]
                cls.DEFINED_GATEWAYS.add(gateway)
                cls.GATEWAYS_SETTINGS[gateway] = {
                    'dtype': lines[i][:-1].split()[-1],
                    'row_index_declaration': i
                }

        # Checking if there is a starte state defined, if not the NoStartStateIsDefinedError is raised.
        if not any([cls.STATES_SETTINGS[state]['start'] for state in cls.DEFINED_STATES]):
            raise NoStartStateIsDefinedError("No state state is defined!")

        # Building the PHOBOS
        row_num = len(cls.DEFINED_STATES)
        col_num = len(cls.ACTIONS)

        # Converting sets into tuples.
        cls.ACTIONS, cls.DEFINED_STATES = tuple(cls.ACTIONS), tuple(cls.DEFINED_STATES)

        # Building the PHOBOS and the mappings dictionaries.
        cls.PHOBOS = [[None for i in range(col_num)] for j in range(row_num)]
        cls.actions_to_index = {action: i for i, action in enumerate(cls.ACTIONS)}
        cls.index_to_action = {i : action for i, action in enumerate(cls.ACTIONS)}
        cls.states_to_index = {state: i for i, state in enumerate(cls.DEFINED_STATES)}

        # Filling up the PHOBOS
        for transition in cls.TEMP_TRANSITIONS:
            cls.PHOBOS[
                cls.states_to_index[transition.split('->')[0].strip()]
            ][
                cls.actions_to_index[cls.TEMP_TRANSITIONS[transition.strip()]]
            ] = transition.split('->')[1].strip()

        for i in range(len(cls.PHOBOS)):
            for j in range(len(cls.PHOBOS[i])):
                if cls.PHOBOS[i][j] is None:
                    cls.PHOBOS[i][j] = cls.DEFINED_STATES[i]

        # Building up the DEIMOS dictionary.
        for i in range(len(cls.PHOBOS)):
            for j in range(len(cls.PHOBOS[i])):
                cls.DEIMOS[tuple([
                    cls.DEFINED_STATES[i], cls.ACTIONS[j]
                ])] = cls.PHOBOS[i][j]

        def __init__(self):
            '''
                The __init__ function of the new created class.
            '''
            self.start_state = None
            # Setting up the initial state the start state of the FSM.
            for state in cls.STATES_SETTINGS:
                if cls.STATES_SETTINGS[state]['start']:
                    self.start_state = state
            # Setting up the functions of the new created class.
            setattr(cls, 'start_state', self.start_state)
            setattr(self, '__change_state', cls.__change_state)
            setattr(self, 'threshold', cls.threshold)
            setattr(self, 'timepassed', cls.timepassed)
            setattr(self, 'equal', cls.equal)
            setattr(self, 'run', cls.run)

        # Setting up the class constructor.
        cls.__init__ = __init__
