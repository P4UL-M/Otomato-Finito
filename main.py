import json
from pyflowchart import *
from myclass import automata, stateName
from pathlib import Path

path = Path(__file__).parent

# Load the JSON file
with open(path / 'FA' / "Int1-2-22.json", encoding="utf-8") as f:
    data = json.load(f)

myAutomata = automata(data)
myAutomata.display(1)
if not myAutomata.isStandard():
    myAutomata.standardize()
if not myAutomata.isDeterministic():
    myAutomata.determinize()
if not myAutomata.isComplete():
    myAutomata.complete()
myAutomata.display(1)
print("recognize :",myAutomata.recognize("AAAABBBBBBBBBBBBBBB"))
#print(myAutomata.isComplete())
#myAutomata.complete()