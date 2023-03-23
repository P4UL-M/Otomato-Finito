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
        try:
            automaton.complementary()
            print("Complementary :")
            automaton.display(1)
        except BadAction as e:
            print(e.args[0])
        automaton = automata(copy.deepcopy(data))
        if "€" in automaton.language:
            automaton.determinize()
        try:
            automaton.minimize()
            print("Minimization :")
            automaton.display(1)
        except Exception as e:
            print(e.args[0])
        # try random strings recognition
        automaton = automata(copy.deepcopy(data))
        if "€" in automaton.language:
            automaton.determinize()
        for i in range(10):
            word = "".join([random.choice(automaton.language) for i in range(random.randint(1, 10))])
            print("The automaton", "does" if automaton.recognize(word) else "does not", "recognize", word)
            
