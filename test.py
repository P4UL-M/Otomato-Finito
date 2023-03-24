from myclass import * 
import pathlib
import json
import copy
from logger import print, var
import random

path = pathlib.Path(__file__).parent

if __name__ == '__main__':
    folder = pathlib.Path(path / "FA")
    files = sorted([*map(lambda x: x.relative_to(folder), filter(lambda x: x.is_file(), folder.rglob("*.txt")))])
    for file in files:
        var.outfile = file
        with open(path / 'FA' / file, encoding="utf-8") as f:
            print(file)
            data:dict = json.load(f)
        original = automata(copy.deepcopy(data))
        automaton = automata(copy.deepcopy(data))
        automaton.display(1)
        try:
            automaton.standardize()
            print("Standardization :")
            automaton.display(1)
        except BadAction as e:
            print(e.args[0])
        automaton = automata(copy.deepcopy(data))
        try:
            automaton.determinize()
            print("Determinization :")
            automaton.display(1)
        except BadAction as e:
            print(e.args[0])
        automaton = automata(copy.deepcopy(data))
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
        minimized = automata(copy.deepcopy(data))
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
        determinized = automata(copy.deepcopy(data))
        if "€" in determinized.language:
            determinized.determinize()
        for i in range(10):
            word = "".join([random.choice(determinized.language) for i in range(random.randint(1, 10))])
            print("The automaton", "does" if determinized.recognize(word) else "does not", "recognize", word)
        for i in range(100000):
            word = "".join([random.choice(automaton.language) for i in range(random.randint(1, 10))])
            if minimized.recognize(word) != original.recognize(word) or automaton.recognize(word) == original.recognize(word):
                print("Error !", word, file, automaton.recognize(word), original.recognize(word), minimized.recognize(word))
                raise Exception("Error !")

