# Otomato-Finito

Otomato-Finito is a simple cli-based program that allows you to create a finite state machine (FSM) and simulate it.

## Installation
You can install Otomato-Finito's dependencies by running the following command:
```pip install -r requirements.txt```

## Usage
To run Otomato-Finito, run the following command:
```python Int1_2_main.py```

### Creating a FSM
You can create a FSM by adding a new file in the ``FA`` folder.
You must respect the format you can see in the ``example_data_format.json`` file.
Your file must be a valid JSON file with extension ``.txt``.

### Exporting a FSM
You can export a FSM in the menu by selecting the option ``Export``.
Requirements:
- The language must have only one letter in its alphabet.
- The FSM must be deterministic.

You can visualize the FSM by copying the output at [Flowchart.js](http://flowchart.js.org/) website.

### Features
You can perform the following actions:
- Standardize the FSM
- Determinize the FSM
- Complete the FSM
- Find the Complement of the FSM
- Minimize the FSM
- Check if a word is accepted by the FSM