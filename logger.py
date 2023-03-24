"""
Ôtomato Finito
CARDONA Quentin, HATOUM Jade, LOONES Axel, MAIRESSE Paul, MALLÉUS Soizic
This file contains a custom print function in order to write the outputs in a file.
"""
from __future__ import print_function
import pathlib
# Python 3
import builtins as __builtin__

class var:
    """A class to store global variables."""
    endfiles: str = []
    outfile: str = ""
    path = pathlib.Path(__file__).parent

def print(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    if var.outfile in var.endfiles:
        with open(var.path / "outputs" / var.outfile, "a") as f:
            sep = kwargs.get("sep", " ")
            f.write(sep.join(map(str,args)) + "\n")
    else:
        with open(var.path / "outputs" / var.outfile, "w+") as f:
            sep = kwargs.get("sep", " ")
            f.write(sep.join(map(str,args)) + "\n")
        var.endfiles.append(var.outfile)
    return __builtin__.print(*args, **kwargs)