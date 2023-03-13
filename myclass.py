from pyflowchart import *
from tabulate import tabulate



class automata():
    def __init__(self, data) -> None:
        self.language: list[str] = data["language"]
        self.states: dict[str, dict[str, list[str]] | bool] = data["states"]
        self.init_state: str = self.findInitState()

    def findInitState(self) -> str:
        initState = None
        for state, properties in self.states.items():
            if properties["start"] and initState == None:
                initState = state
            elif properties["start"] and initState:
                return None
        return initState

    def ifStandard(self) -> bool:
        if self.init_state == None:
            return False
        for state, propreties in self.states.items():
            for letter in self.language:
                for endState in propreties[letter]:
                    if endState == self.init_state:
                        return False
        return True

    def standardize(self) -> None:
        if self.ifStandard():
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

    #TODO : Display - Paul
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

    # TODO : Menu principal - Soizic

    # TODO : Minimize - Jade

    # TODO: Determinize + complete - Quentin
    def complete(self) -> None:
        create = True
        for states in self.states:
            if ("P" in states):
                create = False
        if create:
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
                if (properties[letter] == []):
                    properties[letter] = ["P"]

    # TODO : Complement + Word recognition - Axel
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