import inspect
import re
import pickle
from typing import Callable

from colorit import *
from prettytable import PrettyTable


colorit.init_colorit()

def display_help(commands_description):
    my_table = PrettyTable(["Command Name", "Discription", "Example"])
    [my_table.add_row(i) for i in commands_description]
    my_table.align = 'l'
    return color(my_table, Colors.blue)

def get_command(words: str, commands_dict: dict) -> Callable:
    if words[0] == '':
        raise KeyError ("This command doesn't exist")
    for key in commands_dict.keys():
        try:
            if re.search(fr'\b{words[0].lower()}\b', str(key)):
                func = commands_dict[key]
                return func
        except re.error:
            break
    raise KeyError("This command doesn't exist") 

def goodbye(module_name: str = 'Assistant') -> str:
    module_name = inspect.getmodule(inspect.stack()[1][0]).__name__.split('.')[-1].capitalize()
    if module_name == '__main__':
        module_name = 'Assistant'
    return f'{module_name} app has quit!'

def make_red(message) -> str:
    return color(message, Colors.red)



        