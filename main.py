"""
Ôtomato Finito
CARDONA Quentin, HATOUM Jade, LOONES Axel, MAIRESSE Paul, MALLÉUS Soizic
This file contains the main function for the execution of the program.
"""
import json
from pyflowchart import *
from tool import Automata, BadAction, BadAutomata
from pathlib import Path
from InquirerPy import inquirer, get_style
from art import *
from logger import Settings, print


path = Path(__file__).parent

if __name__ == '__main__':
    tprint("Otomato   Finito\n",font="tarty1", chr_ignore=True, decoration="block")
    print("By CARDONA Quentin, HATOUM Jade, LOONES Axel, MAIRESSE Paul, MALLÉUS Soizic")

    # Setting menu
    tprint("Settings", chr_ignore=True)
    promt = inquirer.checkbox(
        message="Select the settings",
        choices=["Debug mode", "Verbose mode"],
        raise_keyboard_interrupt=False,
        mandatory=False,
        border=True,
        instruction="Use space to select and enter to confirm",
    ).execute()
    if promt:
        if "Debug mode" in promt:
            # enter path to debug file
            filepath = inquirer.filepath(
                message="Enter the path to the debug file (pass if you want to create a new one)",
                validate=lambda x: Path(x).is_file() and Path(x).suffix == ".txt",
                raise_keyboard_interrupt=False,
                mandatory=False,
                default=str(path / "outputs"),
            ).execute()
            if filepath == None:
                folder = Path(path / "outputs")
                new_file = "debug.txt"
                confirm_promt = inquirer.confirm(message="Do you want to the default file at the location : " + str(folder / new_file), raise_keyboard_interrupt=False, mandatory=False).execute()
                if confirm_promt:
                    open(folder / new_file, "w+")
                    Settings.outfile = new_file
                    Settings.debug = True
                    print("Debug mode enabled")
                else:
                    print("Debug mode disabled")
                    Settings.debug = False
            else:
                Settings.outfile = Path(filepath).relative_to(path)
                Settings.debug = True
                print("Debug mode enabled")
        if "Verbose mode" in promt:
            Settings.verbose = True

    # Menu
    menu_on = True
    while menu_on: # Menu loop
        folder = Path(path / "FA")
        files = [*map(lambda x: x.relative_to(folder), filter(lambda x: x.is_file(), folder.rglob("*.txt")))]
        # This function lists the files in the folder "FA" which contains all the automata files
        file_chosen = inquirer.fuzzy(
            message="Which file would you like to import :", # To chose the file to work on
            choices=files,
            default="Int1-2-",
            raise_keyboard_interrupt=False,
            border=True,
        ).execute()

        with open(path / 'FA' / file_chosen, encoding="utf-8") as f:
            data = json.load(f)
        myAutomata = Automata(data)

        while myAutomata != None:
            action = inquirer.select(
                message="What do you want to do ?", # To chose the action to do
                choices=["Displaying FA", "Standardization", "Determinization", "Completion", "Minimization",
                        "Word recognition", "Complementary language","Export to flowchart.js"],
                default="Displaying FA",
                raise_keyboard_interrupt=False,
                mandatory=False
            ).execute()

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
                    myAutomata.minimize()
                    print("Minimization completed !")
                    myAutomata.display(1)
                except BadAction as e:
                    print(e.args[0])
                except BadAutomata as e:
                    print(e.args[0])

            elif action == "Word recognition":
                multiple_letter_language = any([len(l) > 1 for l in myAutomata.language])
                print("Here is the language of the automata :", ", ".join(l for l in myAutomata.language if l != "€"))
                promt = inquirer.text(
                    message="Enter the word you want to recognize :", 
                    validate=lambda x: all([l in myAutomata.language for l in (x.split(",") if multiple_letter_language else x)]),
                ).execute()
                print(f"""Your automata {"does" if myAutomata.recognize(promt, ',' if multiple_letter_language else '') else "doesn't" } recognize "{promt}".""")

            elif action == "Complementary language":
                try:
                    myAutomata.complementary()
                    print("Here is the complement automata :")
                    myAutomata.display(1)
                except BadAutomata as e:
                    print(e.args[0])

            elif action == "Export to flowchart.js":
                print(myAutomata.export())

            if not inquirer.confirm(message="Do you want to continue with this automaton ?", raise_keyboard_interrupt=False, mandatory=False).execute(): # To chose if we want to continue with the modified automaton
                myAutomata = None
        menu_on = inquirer.confirm(message="Do you want to continue with another automaton ?", raise_keyboard_interrupt=False, mandatory=False).execute()

    tprint("Good Bye !", chr_ignore=True)