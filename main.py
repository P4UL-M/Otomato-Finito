import json
from pyflowchart import *
from myclass import automata

# Load the JSON file
with open('exemple_data_format.json') as f:
    data = json.load(f)

myAutomata = automata(data)
# try:
#     myAutomata.standardize()
# except Exception as err:
#     print(err)

myAutomata.determinizeWithEmptyWord()
#print(myAutomata.isComplete())
#myAutomata.complete()
myAutomata.display()
