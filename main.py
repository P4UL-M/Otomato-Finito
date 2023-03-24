import json
from pyflowchart import *
from myclass import automata, BadAction, BadAutomata
from pathlib import Path
from InquirerPy import inquirer, get_style



path = Path(__file__).parent

if __name__ == '__main__':
    menu_on = True
    while menu_on:
        folder = Path(path / "FA")
        files = [*map(lambda x: x.relative_to(folder), filter(lambda x: x.is_file(), folder.rglob("*.txt")))]
        file_chosen = inquirer.fuzzy(
            message="Which file would you like to import :",
            choices=files,
            default="Int1-2-",
            raise_keyboard_interrupt=False,
            border=True,
        ).execute()

        with open(path / 'FA' / file_chosen, encoding="utf-8") as f:
            data = json.load(f)
        myAutomata = automata(data)

        while myAutomata != None:
            action = inquirer.select(
                message="What do you want to do ?",
                choices=["Displaying FA", "Standardization", "Determinization", "Completion", "Minimization",
                        "Word recognition", "Complementary language","Export to flowchart.js", "Exit"],
                default="Displaying FA",
                raise_keyboard_interrupt=False,
                mandatory=False
            ).execute()

            if action == None or action == "Exit":
                menu_on = False
                break

            if action == "Displaying FA":
                myAutomata.display(1)

            elif action == "Standardization":
                try:
                    myAutomata.standardize()
                    print("Standardization completed !")
                    myAutomata.display(1)
                except BadAction as e:
                    print(e.args[0])

            elif action == "Determinization":
                try:
                    myAutomata.determinize()
                    print("Determinization completed !")
                    myAutomata.display(1)
                except BadAction as e:
                    print(e.args[0])

            elif action == "Completion":
                try:
                    myAutomata.complete()
                    print("Completion completed !")
                    myAutomata.display(1)
                except BadAction as e:
                    print(e.args[0])
                except BadAutomata as e:
                    print(e.args[0])

            elif action == "Minimization":
                try:
                    myAutomata.minimize(True)
                    print("Minimization completed !")
                    myAutomata.display(1)
                except BadAction as e:
                    print(e.args[0])
                except BadAutomata as e:
                    print(e.args[0])

            elif action == "Word recognition":
                print("Here is the language of the automata :", ", ".join(l for l in myAutomata.language if l != "€"))
                promt = inquirer.text(
                    message="Enter the word you want to recognize :", 
                    validate=lambda x: all([l in myAutomata.language for l in x])
                ).execute()
                print(f"""Your automata {"does" if myAutomata.recognize(promt) else "doesn't" } recognize "{promt}".""")

            elif action == "Complementary language":
                try:
                    myAutomata.complementary()
                    print("Here is the complement automata :")
                    myAutomata.display(1)
                except BadAutomata as e:
                    print(e.args[0])

            elif action == "Export to flowchart.js":
                print(myAutomata.export())

            if not inquirer.confirm(message="Do you want to continue with this automaton ?").execute():
                myAutomata = None
        menu_on = inquirer.confirm(message="Do you want to continue with another automaton ?").execute()
