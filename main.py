import json
from pyflowchart import *
from myclass import automata, stateName
from pathlib import Path
from InquirerPy import inquirer
from pathlib import Path
import os

path = Path(__file__).parent

if __name__ == '__main__':
    menu_on = True
    while menu_on == True :

        file_chosen = inquirer.fuzzy(
            message="Which file would you like to import :",
            choices=os.listdir("FA"),
            default="Int1-2-",
        ).execute()

        action = inquirer.select(
            message="What do you want to do ?",
            choices=["Displaying FA", "Standardization", "Determinization", "Completion", "Minimization",
                     "Word recognition", "Complementary language"],
        ).execute()
        # confirm = inquirer.confirm(message="Confirm?").execute()
        # if confirm == True :
        with open(path / 'FA' / file_chosen, encoding="utf-8") as f:
            data = json.load(f)
        myAutomata = automata(data)

        if action == "Displaying FA":
            myAutomata.display(1)

        elif action == "Standardization":
            if not myAutomata.isStandard():
                myAutomata.standardize()
                print("Standardization completed !")
                myAutomata.display(1)
            else:
                print("The automata is already standard.")

        elif action == "Determinization":
            if not myAutomata.isDeterministic():
                myAutomata.determinize()
                print("Determinization completed !")
                myAutomata.display(1)
            else:
                print("The automata is already deterministic.")

        elif action == "Completion":
            if not myAutomata.isComplete():
                myAutomata.complete()
                print("Completion completed !")
                myAutomata.display(1)
            else:
                print("The automata is already complete.")

        elif action == "Minimization":
            pass

        elif action == "Word recognition":
            print("recognize :",myAutomata.recognize("AAAABBBBBBBBBBBBBBB"))

        elif action == "Complementary language":
            if not myAutomata.isAsync:
                myAutomata.complementary()
                print("Here is the complement automata :")
                myAutomata.display(1)

        menu_on = inquirer.confirm(message="Do you want to continue ?").execute()

#print(myAutomata.isComplete())
#myAutomata.complete()

