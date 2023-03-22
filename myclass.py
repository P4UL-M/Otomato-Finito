from pyflowchart import *
from tabulate import tabulate
from functools import lru_cache
from logger import print

class BadAutomata(Exception):
    pass

class BadAction(Exception):
    pass

funcs = {}
# wrapper that choose which two function with the same name to execute depending if the automata have empty word expression or not
def emptyWordErrorWrapper(emptyWord:bool):
    def wrapper(func):
        global funcs
        def wrapper2(*args, **kwargs):
            if args[0].isAsync == emptyWord:
                return func(*args, **kwargs)
            else:
                raise BadAutomata(f"This function doesn't work {'without' if emptyWord else 'with'} async automata !")
        if func.__name__ not in funcs.keys():
            funcs[func.__name__] = func
            return wrapper2
        else:
            otherFunc = funcs[func.__name__]
            def wrapper3(*args, **kwargs):
                try:
                    return wrapper2(*args, **kwargs)
                except BadAutomata as err:
                    return otherFunc(*args, **kwargs)
            return wrapper3
    return wrapper

class stateName():
    # a frozenset of strings
    def __init__(self, *names) -> None:
        self.name = frozenset(names)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, stateName):
            return False
        return self.name == __o.name

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __str__(self) -> str:
        return str("".join(sorted(self.name)))
    
    def __repr__(self) -> str:
        return str("".join(sorted(self.name)))
    
    def getPrime(self) -> str:
        return str("".join(sorted(self.name)) + "'")
    
    def __add__(self, __o: object):
        if not isinstance(__o, stateName):
            return NotImplemented
        return stateName(*self.name, *__o.name)
    
    def __iter__(self):
        return iter(self.name)

def stateNameSum(*args:stateName):
    return stateName(*map(str, args))

class automata():
    def __init__(self, data) -> None:
        # set language
        self.language: list[str] = data["language"]
        
        # convert states to frozenset notation
        temp_states:dict[str, dict[str, list[str]] | bool] = data["states"]
        # pass each endState to frozenset
        for state, properties in temp_states.items():
            for letter in self.language:
                if letter in properties.keys():
                    properties[letter] = list(map(lambda x: stateName(x), properties[letter]))
        # pass each state to frozenset
        temp_states = {stateName(state): properties for state, properties in temp_states.items()}
        self.states: dict[stateName, dict[str, list[stateName]] | bool] = temp_states

    def findInitState(self) -> str:
        initState = None
        for state, properties in self.states.items():
            if properties["start"] and initState == None:
                initState = state
            elif properties["start"] and initState:
                return None
        return initState

    @property
    def isAsync(self) -> bool:
        return self._isAsync

    @isAsync.getter
    def isAsync(self) -> bool:
        for letter in self.language:
            if letter == "€":
                return True
        return False

    @property
    def init_state(self) -> stateName:
        return self.init_state
    
    @init_state.getter
    def init_state(self) -> stateName:
        return self.findInitState()

    def isStandard(self) -> bool:
        if self.init_state == None:
            return False
        for state, propreties in self.states.items():
            for letter in self.language:
                if letter in propreties.keys():
                    for endState in propreties[letter]:
                        if endState == self.init_state:
                            return False
        return True

    def standardize(self) -> None:
        if self.isStandard():
            raise BadAction("Your automata is already standard")
        transition = {}
        emptyRecognized = False
        for state,properties in self.states.items():
            if properties["start"]:
                properties["start"] = False
                if properties["end"]:
                    emptyRecognized = True
                for letter in self.language:
                    if letter in properties.keys():
                        transition[letter] = properties[letter]
        state = {
            "start": True,
            "end": emptyRecognized,
            **transition
        }
        self.states[stateName("i")] = state

    @emptyWordErrorWrapper(False)
    def isComplete(self) -> bool:
        for states in self.states.values():
            for letter in self.language:
                if letter not in states.keys() or len(states[letter]) == 0:
                    return False
        return True
    
    @emptyWordErrorWrapper(False)
    def complete(self) -> None:
        if self.isComplete() == True:
            raise BadAction("Your automata is already complete")
        P = {}
        for letter in self.language:
            P[letter] = [stateName("P")]
        p_states = {
            "start": False,
            "end": False,
        }
        P.update(p_states)
        self.states[stateName("P")] = P
        for properties in self.states.values():
            for letter in self.language:
                if letter not in properties.keys() or len(properties[letter]) == 0:
                    properties[letter] = [stateName("P")]

    def isDeterministic(self) -> bool:
        if self.isAsync:
            return False
        for properties in self.states.values():
            for letter in self.language:
                if letter in properties.keys():
                    if (len(properties[letter]) > 1):
                        return False
        return True

    @emptyWordErrorWrapper(False)
    def determinize(self) -> None:
        def determinizeRec(actual_state:stateName, new_automata:dict[stateName, dict[str, list[stateName]] | bool] = {}, start=False) -> dict[str, list[stateName]] | bool:
            # make list of transitions from actual state
            transitions = {}
            isEnd = False
            for state, properties in self.states.items():
                for statepart in actual_state:
                    if statepart in state:
                        for letter in self.language:
                            if letter in properties.keys():
                                transitions[letter] = transitions.get(letter, []) + properties[letter]
                        if properties["end"]:
                            isEnd = True
            # compact transitions
            join_transitions = {}
            for letter in self.language:
                if letter not in transitions.keys():
                    continue
                temp = set(transitions[letter])
                if len(temp) == 0:
                    continue
                else:
                    join_transitions[letter] = [stateNameSum(*temp)]
            # make new states from transitions
            new_states = []
            for letter in self.language:
                if letter in join_transitions.keys():
                        if join_transitions[letter][0] not in new_automata.keys():
                            new_states.append(join_transitions[letter][0])
            # add new states to automata
            if actual_state not in new_automata.keys():
                new_automata[actual_state] = {
                    "start": start,
                    "end": isEnd,
                }
                new_automata[actual_state].update(join_transitions)
            for state in new_states:
                determinizeRec(state, new_automata)
            return new_automata
        if self.isDeterministic():
            raise BadAction("Your automata is already deterministic")
        if self.init_state:
            self.states = determinizeRec(self.init_state, start=True)
        else:
            init_states = stateNameSum([state for state,properties in self.states.items() if properties["start"]])
            self.states = determinizeRec(init_states, start=True)

    @emptyWordErrorWrapper(True)
    def determinize(self) -> None:
        if self.isDeterministic():
            raise BadAction("Your automata is already deterministic")
        prime_states: dict[stateName, set[stateName]] = {}
        starting_states = [state for state,properties in self.states.items() if properties["start"]]
        prime_states[stateName(*[s.getPrime() for s in starting_states])] = self._computeEpsilonClosure(*starting_states)
        new_automaton = {}
        isInit = True
        while prime_states:
            state, englobed_states = prime_states.popitem()
            if state in new_automaton.keys():
                continue
            new_state = {}
            for letter in self.language:
                if letter == "€":
                    continue
                next_states:set[stateName] = set()
                for s in englobed_states:
                    next_states.update(self._computeNextStates(s, letter))
                if len(next_states) > 0:
                    new_prime_state_name = stateName(*[s.getPrime() for s in next_states])
                    new_state[letter] = [new_prime_state_name]
                    prime_states[new_prime_state_name] = self._computeEpsilonClosure(*next_states)
            new_state["start"] = isInit
            new_state["end"] = any(self.states[s]["end"] for s in englobed_states)
            isInit = False
            new_automaton[state] = new_state
        self.states = new_automaton
        self.language.remove("€")

    @emptyWordErrorWrapper(False)
    def complementary(self) -> None:
        if not self.isComplete():
            self.complete()
        for properties in self.states.values():
            properties["end"] = not properties["end"]

    # cache for epsilon closure
    @emptyWordErrorWrapper(True)
    @lru_cache(maxsize=None)
    def _computeEpsilonClosure(self, *states:stateName) -> set[stateName]:
        """Compute the ε-closure of a set of states"""
        epsilon_closure = set(states)
        while True:
            new_states = set()
            for state in epsilon_closure:
                if "€" in self.states[state]:
                    new_states.update(self.states[state]["€"])
            new_states.difference_update(epsilon_closure)
            if not new_states:
                break
            epsilon_closure.update(new_states)
        return epsilon_closure

    def _computeNextStates(self, state, letter) -> set[stateName]:
        """Compute the next states for a given state and letter"""
        if letter in self.states[state]:
            return set(self.states[state][letter])
        return set()

    @emptyWordErrorWrapper(False)
    def recognize(self, word:str) -> bool:
        def recognizeRec(state:str, word:str) -> bool:
            if word == "":
                return self.states[state]["end"]
            else:
                if word[0] not in self.language:
                    raise Exception("The word contains a letter that is not in the language of the automata")
                if word[0] not in self.states[state].keys():
                    return False
                else:
                    for endState in self.states[state][word[0]]:
                        if recognizeRec(endState, word[1:]):
                            return True
                    return False
        if self.init_state:
            return recognizeRec(self.init_state, word)
        else:
            init_states = [state for state,properties in self.states.items() if properties["start"]]
            return any(map(lambda state: recognizeRec(state, word), init_states))

    @emptyWordErrorWrapper(True)
    def recognize(self, word:str) -> bool: # function to recognize a word with the empty word expression in the automata
        def recognizeRec(state:stateName, word:str) -> bool:
            if word == "":
                if "€" in self.states[state]:
                    for endState in self.states[state]["€"]:
                        if recognizeRec(endState, word):
                            return True
                return self.states[state]["end"]
            else:
                if word[0] not in self.language:
                    raise Exception("The word contains a letter that is not in the language of the automata")
                if "€" in self.states[state]:
                    for endState in self.states[state]["€"]:
                        if recognizeRec(endState, word):
                            return True
                if word[0] not in self.states[state].keys():
                    return False
                else:
                    for endState in self.states[state][word[0]]:
                        if recognizeRec(endState, word[1:]):
                            return True
                    return False
        if self.init_state:
            return recognizeRec(self.init_state, word)
        else:
            init_states = [state for state,properties in self.states.items() if properties["start"]]
            return any(map(lambda state: recognizeRec(state, word), init_states))

    def display(self, style=0) -> None:
        styles = ["fancy_grid", "rounded_grid", "mixed_grid"]
        table = []
        for state,properties in self.states.items():
            line = [str(state)]
            for letter in self.language:
                if letter in properties.keys():
                    linestr = ", ".join(map(str,properties[letter]))
                else:
                    linestr = ""
                line.append(linestr)
            if properties["start"]:
                line.append("\u2713")
            else:
                line.append("")
            if properties["end"]:
                line.append("\u2713")
            else:
                line.append("")
            table.append(line)
        print(tabulate(table,headers=["State"]+self.language + ["Start", "End"],tablefmt=styles[style]))

    # TODO: correct the export to work with the new stateName class
    def export(self) -> str:
        if not self.init_state:
            raise BadAction(
                "Your automata must at least be standard to be export.")

        nodes: dict[str, OperationNode] = {}

        for state, property in self.states.items():
            if property["start"]:
                nodes[state] = StartNode(state)
            elif property["end"]:
                nodes[state] = EndNode(state)
            else:
                nodes[state] = OperationNode(state)

        for state, propreties in self.states.items():
            for letter in self.language:
                for endState in propreties[letter]:
                    nodes[state].connect(nodes[endState])

        chart = Flowchart(nodes[self.init_state])
        return chart.flowchart()