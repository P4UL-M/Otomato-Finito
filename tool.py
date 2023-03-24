"""
Ôtomato Finito
CARDONA Quentin, HATOUM Jade, LOONES Axel, MAIRESSE Paul, MALLÉUS Soizic
This files contains the class automata and all the functions that are used to manipulate it.
"""
from pyflowchart import *
from tabulate import tabulate
from functools import lru_cache
from logger import print, Settings


class BadAutomata(Exception): # Exception for async automata in functions that don't work with them
    pass

class BadAction(Exception): # Exception for actions that can't be done on the automata
    pass

funcs = {}
# wrapper that chooses which two functions with the same name to execute depending if the automata have empty word expression or not
# display error if function doesn't work with async automata
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
    # a frozenset of strings to manipulate easily grouped states with all default functions to facilitate the use of stateName
    def __init__(self, *names) -> None:
        self.name = frozenset(names)

    # equality function
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, stateName):
            return False
        return self.name == __o.name

    # hash function for dict, set, ...
    def __hash__(self) -> int:
        return hash(self.name)
    
    # string representation for print
    def __str__(self) -> str:
        return str("".join(sorted(self.name)))
    
    # string representation for debug
    def __repr__(self) -> str:
        return str("".join(sorted(self.name)))
    
    # string representation for prime state
    def getPrime(self) -> str:
        return str("".join(sorted(self.name)) + "'")
    
    # concatenation of two stateName
    def __add__(self, __o: object):
        if not isinstance(__o, stateName):
            return NotImplemented
        return stateName(*self.name, *__o.name)
    
    # iterator for states that compose the stateName
    def __iter__(self):
        return iter(self.name)

def stateNameSum(*args:stateName):
    # To sum a list of stateName to a single stateName
    return stateName(*map(str, args))

class Automata():
    # class that contains all the functions to manipulate automata
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

    # function to get the initial state of the automata, returns None if there is more than one
    def findInitState(self) -> str:
        # find the initial state and returns none if there is more than one
        initState = None
        for state, properties in self.states.items():
            if properties["start"] and initState == None:
                initState = state
            elif properties["start"] and initState:
                return None
        return initState
    
    # function to get the final states of the automata
    def findFinalStates(self) -> set[stateName]:
        # find all the final states
        FinalStates = set()
        for state, properties in self.states.items():
            if properties["end"]:
                FinalStates.add(state)
        return FinalStates

    # property to check if the automata is async
    @property
    def isAsync(self) -> bool:
        return self._isAsync

    @isAsync.getter
    def isAsync(self) -> bool:
        # check if the automata is async
        return "€" in self.language

    # property to get the initial state of the automata
    @property
    def init_state(self) -> stateName:
        return self.init_state
    
    @init_state.getter
    def init_state(self) -> stateName:
        # get the initial state of the automata
        return self.findInitState()

    # function to check if the automata is standard
    def isStandard(self) -> bool:
        # check if the automata is standard
        if self.init_state == None:
            return False # if there is more than one initial state
        for state, propreties in self.states.items():
            for letter in self.language:
                if letter in propreties.keys():
                    for endState in propreties[letter]:
                        if endState == self.init_state:
                            return False # if there is a transition to the initial state
        return True

    def standardize(self) -> None:
        # standardize the automata if not already standard
        if self.isStandard():
            raise BadAction("Your automata is already standard")
        transition = {}
        emptyRecognized = False
        # get all the transitions to the initial state
        for state,properties in self.states.items():
            if properties["start"]:
                properties["start"] = False
                if properties["end"]:
                    emptyRecognized = True
                for letter in self.language:
                    if letter in properties.keys():
                        transition[letter] = properties[letter]
        # create the new initial state
        state = {
            "start": True,
            "end": emptyRecognized,
            **transition
        }
        # add the new initial state to the automata
        self.states[stateName("i")] = state

    @emptyWordErrorWrapper(False) # async automata can't be complete
    def isComplete(self) -> bool:
        # check if the automata is complete
        for states in self.states.values():
            for letter in self.language:
                if letter not in states.keys() or len(states[letter]) == 0:
                    return False # if there is a state that doesn't have a transition for a letter
        return True
    
    @emptyWordErrorWrapper(False) # async automata can't be complete
    def complete(self) -> None:
        # complete the automata  for not async automata if not already complete
        if self.isComplete() == True:
            raise BadAction("Your automata is already complete")
        # create the trash state
        P = {}
        for letter in self.language:
            P[letter] = [stateName("P")]
        P.update({
            "start": False,
            "end": False,
        })
        self.states[stateName("P")] = P
        for properties in self.states.values():
            for letter in self.language:
                if letter not in properties.keys() or len(properties[letter]) == 0:
                    properties[letter] = [stateName("P")] # add a transition to the trash state for each letter that doesn't have a transition

    def isDeterministic(self) -> bool:
        # check if the automata is deterministic
        if self.isAsync:
            return False # async automata can't be deterministic
        if self.init_state == None:
            return False # if there is more than one initial state
        for properties in self.states.values():
            for letter in self.language:
                if letter in properties.keys():
                    if (len(properties[letter]) > 1):
                        return False # if there is a state that has more than one transition for a letter
        return True

    @emptyWordErrorWrapper(False) # normal automata function
    def determinize(self) -> None:
        # determinize the automata for not async automata if not already deterministic
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
                determinizeRec(state, new_automata) # recursive call for new states
            return new_automata
        if self.isDeterministic():
            raise BadAction("Your automata is already deterministic")
        if self.init_state: # if there is only one initial state
            self.states = determinizeRec(self.init_state, start=True)
        else:
            # if there is more than one initial state, combine them into one
            init_states = stateNameSum(*[state for state,properties in self.states.items() if properties["start"]])
            self.states = determinizeRec(init_states, start=True)

    @emptyWordErrorWrapper(True) # async automata function
    def determinize(self) -> None:
        # determinize the automata for async automata if not already deterministic
        if self.isDeterministic():
            raise BadAction("Your automata is already deterministic")
        # create list of new states
        prime_states: dict[stateName, set[stateName]] = {} # prime states are the epsilon closure of the states
        # get all the starting states
        starting_states = [state for state,properties in self.states.items() if properties["start"]]
        # create the new initial state
        prime_states[stateName(*[s.getPrime() for s in starting_states])] = self._computeEpsilonClosure(*starting_states)
        new_automaton = {}
        isInit = True # add a flag to know if the state is the initial state
        while prime_states: # while there is still new states to process
            state, englobed_states = prime_states.popitem()
            if state in new_automaton.keys(): # if the state has already been processed
                continue
            new_state = {} # create the new state
            for letter in self.language:
                if letter == "€": # if the letter is the empty word we don't need to compute the next states
                    continue
                next_states:set[stateName] = set()
                for s in englobed_states:
                    next_states.update(self._computeNextStates(s, letter))
                if len(next_states) > 0:
                    new_prime_state_name = stateName(*[s.getPrime() for s in next_states])
                    new_state[letter] = [new_prime_state_name]
                    prime_states[new_prime_state_name] = self._computeEpsilonClosure(*next_states) # add the new state to the list of new states
            new_state["start"] = isInit
            new_state["end"] = any(self.states[s]["end"] for s in englobed_states) # if one of the states is an end state, the new state is an end state
            isInit = False # the initial state has been added
            new_automaton[state] = new_state # add the new state to the automaton
        self.states = new_automaton # replace the old automaton with the new one
        self.language.remove("€") # remove the empty word from the language

    @emptyWordErrorWrapper(False) # async automata can't be complete so we can't get the complement
    def complementary(self) -> None:
        if not self.isDeterministic(): # automata need to be deterministic to obtain the complement
            raise BadAction("Please determinize the automaton before making its complementary")
        if not self.isComplete():
            self.complete() # adding missing transitions which will be needed to make the complement
        for properties in self.states.values():
            properties["end"] = not properties["end"] # invert the end state

    @emptyWordErrorWrapper(False)
    def minimize(self) -> None:
        # make sure we have a CDFA
        condition = []
        if not self.isDeterministic(): # automata need to be deterministic to minimize it
            condition += ["determinize"]
        if not self.isComplete(): # automata need to be complete to minimize it
            condition += ["complete"]
        if condition:
            raise BadAction(f"Please { ' and '.join(map(str,condition)) } the automaton before minimizing it!")
        
        # construct the initial partition (Θ0 = {F, NF})
        F = self.findFinalStates()# final states
        NF = set(self.states.keys()) - F # non-final states
        θcurrent : list[set:stateName] = [group for group in [F, NF] if group] # exclude empty sets in θcurrent
        θprev : list[set:stateName] = []
        i=0 # iteration counter
        
        while θprev != θcurrent: # while the partition is not stable
            if len(θprev) == len(self.states): # if the partition has as many groups as states
                raise BadAction("The automaton is already minimal!")

            θprev = θcurrent # store current partition to compare it to the next partition
            
            groupNames = {stateName(f"({num})") : group for num,group in enumerate(θcurrent)}
            subgroups: list[set[stateName]] = []

            for groupStateNames in θprev: # for each group in the current partition
                groupStates : dict[stateName:dict[str:list[stateName]|bool]] = {key: self.states[key] for key in groupStateNames}
                
                if len(groupStates) > 1: # if the group isn't a singleton
                    #logic :
                    partitionStates = {}
                    for state, properties in groupStates.items():
                        new_transitions = {}
                        for letter in self.language:
                            if letter in properties.keys():
                                new_transitions[letter] = [groupName for groupName, group in groupNames.items() if properties[letter][0] in group]
                        partitionStates[state] = new_transitions
                    
                    if Settings.verbose: # print each partition
                        # original table
                        table = []
                        for state, properties in groupStates.items():
                            line = [str(state)]
                            for letter in self.language:
                                if letter in properties.keys(): # if the state has a transition for the letter
                                    line.append(", ".join(map(str,properties[letter])) )
                            table.append(line)
                                        
                        # under θi : check in which groups are the states in table2
                        partitionTable = []
                        for state in groupStates.keys():
                            partitionLine = []
                            for letter in self.language:
                                partitionLine.append(partitionStates[state][letter][0])
                            partitionTable.append(partitionLine)
                        
                        table1 = tabulate(table, headers = ["State"]+self.language, tablefmt="rounded_grid")
                        table2 = tabulate(partitionTable, headers = self.language, tablefmt="rounded_grid")

                        # print title in bold, red and underlined
                        print(f" \033[1m\033[4m\033[31mIteration θ {i} :\033[0m")
                        print(tabulate( [ [key , ", ".join(map(str,val))] for key,val in groupNames.items() ] ,headers = ['Group names','States contained'],tablefmt="rounded_grid"),end="\n")
                        print(tabulate([[table1, table2]],headers = ['Original',f'Under θ {i}'],tablefmt="rounded_grid"),end="\n\n\n")
                        # to print the tables of the groups in the partition and the corresponding transition table
                
                    currentSubgroups: list[list[stateName]] = []
                    for state, transtitions in partitionStates.items(): # this loop is to group the states in the current group
                        if len(currentSubgroups) == 0:
                            currentSubgroups.append([state])
                            continue
                        added = False
                        for subgroup in currentSubgroups:
                            equal = True
                            for letter in self.language:
                                if transtitions[letter] != partitionStates[subgroup[-1]][letter]:
                                    equal = False
                                    break
                            if equal:
                                added = True
                                subgroup.append(state)
                                break
                        else:
                            if not added:
                                currentSubgroups.append([state])
                    for subgroup in currentSubgroups:
                        subgroups.append(subgroup)
                        
                else: # if the group is a singleton
                    subgroups.append(groupStateNames)
                    
            θcurrent = subgroups
            i += 1
        if len(θcurrent) == len(self.states): # if we obtain the same number of groups as states then the automaton is already minimal
            raise BadAction("The automaton is already minimal!")
        # create the new automaton
        new_automaton = {}
        for group in θcurrent: # compute the new states transitions and properties
            new_state = {}
            new_state["start"] = any(self.states[s]["start"] for s in group)
            new_state["end"] = any(self.states[s]["end"] for s in group)
            # create new transitions
            for letter in self.language:
                for state in group:
                    if letter in self.states[state]:
                        new_state[letter] = [groupName for groupName, group in groupNames.items() if self.states[state][letter][0] in group]
                        break
            group_name = [groupName for groupName, group in groupNames.items() if state in group][0]
            new_automaton[group_name] = new_state
        self.states = new_automaton # replace the old automaton with the new one
        
    @emptyWordErrorWrapper(True)
    @lru_cache(maxsize=None) # cache for epsilon closure so that it is computed only once for each state
    def _computeEpsilonClosure(self, *states:stateName) -> set[stateName]:
        """Compute the ε-closure of a set of states"""
        epsilon_closure = set(states)
        while True: 
            new_states = set() # new states to add to the epsilon closure
            for state in epsilon_closure:
                if "€" in self.states[state]:
                    new_states.update(self.states[state]["€"])
            new_states.difference_update(epsilon_closure)
            if not new_states:
                break # if there are no new states to add to the epsilon closure
            epsilon_closure.update(new_states) # add the new states to the epsilon closure
        return epsilon_closure # return the epsilon closure

    def _computeNextStates(self, state, letter) -> set[stateName]:
        """Compute the list of next states for a given state and letter"""
        if letter in self.states[state]:
            return set(self.states[state][letter]) # return the next states if there is a transition for the letter as a set
        return set()

    @emptyWordErrorWrapper(False)
    def recognize(self, word:str) -> bool:
        """Recognize a word with the automaton if it is not async"""
        def recognizeRec(state:str, word:str) -> bool:
            if word == "": # if the word is empty, return true if the state is an end state
                return self.states[state]["end"]
            else:
                if word[0] not in self.language:
                    raise Exception("The word contains a letter that is not in the language of the automata") # if the word contains a letter that is not in the language of the automata, raise an exception
                if word[0] not in self.states[state].keys():
                    return False # if there is no transition for the letter, return false
                else:
                    for endState in self.states[state][word[0]]:
                        if recognizeRec(endState, word[1:]):
                            return True # if any of the next states can recognize the rest of the word, return true
                    return False # if none of the next states can recognize the rest of the word, return false
        if self.init_state:
            return recognizeRec(self.init_state, word) # if there is an initial state, start from it
        else:
            init_states = [state for state,properties in self.states.items() if properties["start"]] # else test from all the initial states
            return any(map(lambda state: recognizeRec(state, word), init_states)) # return true if any of the initial states can recognize the word

    @emptyWordErrorWrapper(True)
    def recognize(self, word:str) -> bool: # function to recognize a word with the empty word expression in the automata
        """Recognize a word with the automaton if it is async"""
        def recognizeRec(state:stateName, word:str) -> bool:
            if word == "":
                if "€" in self.states[state]:
                    for endState in self.states[state]["€"]:
                        if recognizeRec(endState, word):
                            return True # if the word is empty and there is an empty word transition, return true if any of the next states can recognize the empty word
                return self.states[state]["end"]
            else: # same as the non async version
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
            return recognizeRec(self.init_state, word) # if there is an initial state, start from it
        else:
            init_states = [state for state,properties in self.states.items() if properties["start"]] # else test from all the initial states
            return any(map(lambda state: recognizeRec(state, word), init_states)) # return true if any of the initial states can recognize the word

    def display(self, style=0) -> None:
        """Display the automaton in a table with different styles"""
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

    def export(self) -> str:
        """Export the automaton as a flowchart"""
        if not self.isDeterministic():
            raise BadAction("The automaton is not deterministic")
        if len(self.language) > 1:
            raise BadAction("The automaton must have a language of size 1")

        # create the nodes of the flowchart
        nodes: dict[str, OperationNode] = {}

        # add each state as a node
        for state, property in self.states.items():
            if property["start"]:
                nodes[state] = OperationNode(str(state) + " (start)")
            elif property["end"]:
                nodes[state] = OperationNode(str(state) + " (end)")
            else:
                nodes[state] = OperationNode(state)

        # add the transitions
        for state, propreties in self.states.items():
            for letter in self.language:
                if letter in propreties.keys():
                    for endState in propreties[letter]:
                        nodes[state].connect(nodes[endState])

        # create the flowchart
        chart = Flowchart(nodes[self.init_state])
        return chart.flowchart() # return the flowchart
