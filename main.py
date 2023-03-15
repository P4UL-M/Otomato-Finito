import json
from pyflowchart import *
from myclass import automata

# Load the JSON file
with open('FA/Int1-2-44.json') as f:
    data = json.load(f)

myAutomata = automata(data)
# try:
#     myAutomata.standardize()
# except Exception as err:
#     print(err)

# print(myAutomata.recognize('AAAAAA'))
#print(myAutomata.isComplete())
#myAutomata.complete()
myAutomata.display(1)
