import re
from typing import Callable
import pickle

from . import common
from . import notepad
from . import  addressbook
from . import sort
from .abstract_ui import UI



class UserInterfaceMain(UI):
    def greeting(self):
        return ('Hi there! Welcome to the Assistant app. Enter the command from the table above.')
    
    def goodbye(self):
        return common.goodbye()
    
    def display_help(self):
        return common.display_help(commands_description)
    

ui = UserInterfaceMain()

commands_dict = {
                 ('1',): notepad.main,
                 ('2',): addressbook.main,
                 ('3',): sort.main,
                 ('goodbye','close','exit','quit'):ui.goodbye
}

commands_description = [['1', "Open the Notepad app", '1'], 
                        ['2', "Open the Addressbook app", '2'], 
                        ['3', "Open the Sort app (sorts files in a provided directory)", '3'], 
                        ['goodbye/close/exit/quit', "Quit the Assistant", 'quit']

]



def main():
    print(ui.display_help())
    print(ui.greeting())
    while True:
        words = input('What do you want to do? ').split(' ')
        try:
            command = common.get_command(words, commands_dict)   
        except KeyError as err:
            print(err)
            continue
        command()
        if command.__name__ == 'goodbye':
            print(command())
            break
        
if __name__ == '__main__':
    main()





