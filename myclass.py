from pyflowchart import *
from tabulate import tabulate

class automata():
    def __init__(self,data) -> None:
        self.language:list[str] = data["language"]
        self.states:dict[str,dict[str,list[str]]|bool] = data["states"]
        self.init_state:str = self.findInitState()

    def findInitState(self) -> str:
        initState = None
        for state,properties in self.states.items():
            if properties["start"] and initState==None:
                initState = state
            elif properties["start"] and initState:
                return None
        return initState

    def ifStandard(self) -> bool:
        if self.init_state==None:
            return False
        for state,propreties in self.states.items():
            for letter in self.language:
                for endState in propreties[letter]:
                    if endState == self.init_state:
                        return False
        return True
    
    def standardize(self) -> None:
        if self.ifStandard():
            raise Exception("Your automata is already standard")
        transition = {}
        for state,properties in self.states.items():
            if properties["start"]:
                properties["start"] = False
                for letter in self.language:
                    transition[letter] = properties[letter]
        state = {
            "start": True,
            "end": False,
        }
        state.update(transition)
        self.states["i"] = state
        self.init_state = "i"

    #TODO : Menu principal - Soizic

    #TODO : Display - Paul
    def display(self) -> None:
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
        print(tabulate(table,headers=["State"]+self.language + ["Start", "End"],tablefmt="fancy_grid"))

    #TODO : Minimize - Jade

    #TODO : Complement + Word recognition - Axel

    #TODO: Determinize + complete - Quentin

    def export(self) -> str:
        if not self.init_state:
            raise Exception("Your automata must at least be standard to be export.")
        
        nodes:dict[str,OperationNode] = {}

        for state,property in self.states.items():
            if property["start"]:
                nodes[state] = StartNode(state)
            elif property ["end"]:
                nodes[state] = EndNode(state)
            else:
                nodes[state] = OperationNode(state)

        for state,propreties in self.states.items():
            for letter in self.language:
                for endState in propreties[letter]:
                    nodes[state].connect(nodes[endState])

        chart = Flowchart(nodes[self.init_state])
        return chart.flowchart()
