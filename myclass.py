from pyflowchart import *
from tabulate import tabulate

funcs = {}
# wrapper that choose which two function with the same name to execute depending if the automata have empty word expression or not
def emptyWordErrorWrapper(emptyWord:bool):
    def wrapper(func):
        global funcs
        def wrapper2(*args, **kwargs):
            if args[0].emptyWordExpression == emptyWord:
                return func(*args, **kwargs)
            else:
                raise Exception(f"This function doesn't work {'without' if emptyWord else 'with'} empty word expression")
        if func.__name__ not in funcs.keys():
            funcs[func.__name__] = func
            return wrapper2
        else:
            otherFunc = funcs[func.__name__]
            def wrapper3(*args, **kwargs):
                try:
                    return wrapper2(*args, **kwargs)
                except Exception as err:
                    return otherFunc(*args, **kwargs)
            return wrapper3
    return wrapper

class automata():
    def __init__(self, data) -> None:
        self.language: list[str] = data["language"]
        self.states: dict[str, dict[str, list[str]] | bool] = data["states"]
        self.init_state: str = self.findInitState()
        self.emptyWordExpression = self.checkEmptyWordExpression()
        # sort states letters
        for properties in self.states.values():
            for letter in self.language:
                if letter in properties.keys():
                    properties[letter].sort()

    def findInitState(self) -> str:
        initState = None
        for state, properties in self.states.items():
            if properties["start"] and initState == None:
                initState = state
            elif properties["start"] and initState:
                return None
        return initState

    def checkEmptyWordExpression(self) -> bool:
        for letter in self.language:
            if letter == "€":
                return True
        return False

    @emptyWordErrorWrapper(False)
    def isStandard(self) -> bool:
        if self.init_state == None:
            return False
        for state, propreties in self.states.items():
            for letter in self.language:
                for endState in propreties[letter]:
                    if endState == self.init_state:
                        return False
        return True

    @emptyWordErrorWrapper(False)
    def standardize(self) -> None:
        if self.isStandard():
            raise Exception("Your automata is already standard")
        transition = {}
        emptyRecognized = False
        for state,properties in self.states.items():
            if properties["start"]:
                properties["start"] = False
                if properties["end"]:
                    emptyRecognized = True
                for letter in self.language:
                    transition[letter] = properties[letter]
        state = {
            "start": True,
            "end": emptyRecognized,
        }
        state.update(transition)
        self.states["i"] = state
        self.init_state = "i"

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
            return
        P = {}
        for letter in self.language:
            P[letter] = ["P"]
        p_states = {
            "start": False,
            "end": False,
        }
        P.update(p_states)
        self.states["P"] = P
        for properties in self.states.values():
            for letter in self.language:
                if letter not in properties.keys() or len(properties[letter]) == 0:
                    properties[letter] = ["P"]

    @emptyWordErrorWrapper(False)
    def isDeterministic(self) -> bool:
        for states in self.states.values():
            for letter in self.language:
                if letter in states.keys():
                    if (len(states[letter]) > 1):
                        return False
        return True

    @emptyWordErrorWrapper(False)
    def determinize(self) -> None:
        def determinizeRec(actual_state:str, new_automata:dict[str, dict[str, list[str]] | bool] = {}, start=False) -> str:
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
                    join_transitions[letter] = []
                    continue
                temp = list(set(transitions[letter]))
                temp.sort()
                if len(temp) == 0:
                    join_transitions[letter] = []
                else:
                    join_transitions[letter] = ["".join(temp)]
            # make new states from transitions
            new_states = []
            for letter in self.language:
                if len(join_transitions[letter]) > 0:
                    if join_transitions[letter][0] != "":
                        new_states.append("".join(join_transitions[letter][0]))
            # add new states to automata
            if actual_state not in new_automata.keys():
                new_automata[actual_state] = {
                    "start": start,
                    "end": isEnd,
                }
                new_automata[actual_state].update(join_transitions)
            for state in new_states:
                if state not in new_automata.keys():
                    determinizeRec(state, new_automata)
            return new_automata
        if self.isDeterministic():
            raise Exception("Your automata is already deterministic")
        if self.init_state:
            self.states = determinizeRec(self.init_state, start=True)
        else:
            init_states = "".join([state for state,properties in self.states.items() if properties["start"]])
            self.states = determinizeRec(init_states, start=True)

    @emptyWordErrorWrapper(True)
    def determinize(self) -> None:
        # Create a new start state and add the old start state to it
        new_start_state = "i"
        self.states[new_start_state] = {"start": True, "end": False}
        self.states[new_start_state].update({letter: [] for letter in self.language})
        self.states[new_start_state]["€"] = [self.init_state]
        # Compute ε-closure for the new start state
        epsilon_closure = self.computeEpsilonClosure([new_start_state])
        # Initialize the new automaton
        new_automaton = {"i": {"start": True, "end": self.containsEndState(epsilon_closure)}}
        for letter in self.language:
            new_automaton["i"][letter] = self.computeNextState(epsilon_closure, letter)
        new_states = ["i"]
        # Add new states to the new automaton
        while new_states:
            state = new_states.pop()
            for letter in self.language:
                next_state = self.computeNextState(self.computeEpsilonClosure(list(state)), letter)
                if next_state:
                    next_state = "".join(sorted(next_state))
                    if next_state not in new_automaton:
                        new_automaton[next_state] = {"start": False, "end": self.containsEndState(next_state)}
                        for letter in self.language:
                            new_automaton[next_state][letter] = ["".join(sorted(self.computeNextState(next_state, letter)))]
                        new_states.append(next_state)
        # Update the current automaton
        self.states = new_automaton
        self.init_state = new_start_state
        self.emptyWordExpression = False

    @emptyWordErrorWrapper(True)
    def computeEpsilonClosure(self, states):
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

    def computeNextState(self, states, letter):
        """Compute the next state from a set of states and a letter"""
        next_states = set()
        for state in states:
            if letter in self.states[state]:
                next_states.update(self.states[state][letter])
        return next_states

    def containsEndState(self, states):
        """Check if a set of states contains an end state"""
        for state in states:
            if self.states[state]["end"]:
                return True
        return False

    @emptyWordErrorWrapper(False)
    def recognize(self, word:str) -> bool:
        def recognizeRec(state:str, word:str) -> bool:
            if word == "":
                return self.states[state]["end"]
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
            line = [state]
            for letter in self.language:
                linestr = ", ".join(properties[letter])
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

    def export(self) -> str:
        if not self.init_state:
            raise Exception(
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