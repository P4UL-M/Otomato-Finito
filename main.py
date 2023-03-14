import json
from pyflowchart import *
from myclass import automata, stateName

# Load the JSON file
with open('exemple_data_format.json') as f:
    data = json.load(f)

name = stateName("1'", "2'")
name2 = stateName("2")
name3 = stateName("2", "1")

myset = set([name, name2, name3])

myAutomata = automata(data)
# try:
#     myAutomata.standardize()
# except Exception as err:
#     print(err)
myAutomata.display(1)
myAutomata.determinize()
myAutomata.display(1)
print(myAutomata.isDeterministic())
print(myAutomata.recognize("AAAABBBBBBBBBBBBBBB"))
#print(myAutomata.isComplete())
#myAutomata.complete()