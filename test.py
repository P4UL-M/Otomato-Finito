from tool import * 
import pathlib
import json
import copy
from logger import print, Settings
import random

path = pathlib.Path(__file__).parent

if __name__ == '__main__':
    # set debug mode
    Settings.debug = True
    Settings.verbose = True
    # set the output file
    folder = pathlib.Path(path / "FA")
    # get all the files in the folder
    files = sorted([*map(lambda x: x.relative_to(folder), filter(lambda x: x.is_file(), folder.rglob("*.txt")))])
    # iterate over all the files
    for file in files:
        Settings.outfile = file
        with open(path / 'FA' / file, encoding="utf-8") as f:
            print(file)
            data:dict = json.load(f)
        original = Automata(copy.deepcopy(data)) # original automaton
        automaton = Automata(copy.deepcopy(data)) # automaton to test standardization
        automaton.display(1)
        try:
            automaton.standardize()
            print("Standardization :")
            automaton.display(1)
        except BadAction as e:
            print(e.args[0])
        automaton = Automata(copy.deepcopy(data)) # automaton to test determinization
        try:
            automaton.determinize()
            print("Determinization :")
            automaton.display(1)
        except BadAction as e:
            print(e.args[0])
        automaton = Automata(copy.deepcopy(data)) # automaton to test completion and complementary
        if "€" in automaton.language:
            automaton.determinize()
        try:
            automaton.complete()
            print("Completion :")
            automaton.display(1)
        except BadAction as e:
            print(e.args[0])
        if not automaton.isDeterministic():
            automaton.determinize()
        try:
            automaton.complementary()
            print("Complementary :")
            automaton.display(1)
        except BadAction as e:
            print(e.args[0])
        minimized = Automata(copy.deepcopy(data)) # automaton to test minimization
        if not minimized.isDeterministic():
            minimized.determinize()
        if not minimized.isComplete():
            minimized.complete()
        try:
            minimized.minimize()
            print("Minimization :")
            minimized.display(1)
        except Exception as e:
            print(e.args[0])
        # try random strings recognition
        determinized = Automata(copy.deepcopy(data)) # determinized automaton to optimize recognition speed
        if not determinized.isDeterministic():
            determinized.determinize()
        for i in range(10):
            word = "".join([random.choice(determinized.language) for i in range(random.randint(1, 10))])
            print("The automaton", "does" if determinized.recognize(word) else "does not", "recognize", word)
        for i in range(100000): # test 100000 random words for each function to check if the new automaton is correct
            word = "".join([random.choice(automaton.language) for i in range(random.randint(1, 10))])
            if minimized.recognize(word) != original.recognize(word) or automaton.recognize(word) == original.recognize(word):
                print("Error !", word, file, automaton.recognize(word), original.recognize(word), minimized.recognize(word))
                raise Exception("Error !")

