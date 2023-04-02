import calendar
import functools
import pickle
import re
from datetime import datetime
from collections import UserDict
from typing import Callable

from colorit import *
from prettytable import PrettyTable
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt

from . import common
from .abstract_ui import UI


class MyException(Exception):
    pass

class AddressBook(UserDict):
    
    index: str = 0
        
    def __getitem__(self, name):
        if not name in self.data.keys():
            raise MyException("This user isn't in the Book")
        user = self.data[name]
        return user
 
    def add_record(self, record) -> str:
        self.data.update({record.name.value:record})
        return 'Done!'
    
    def delete_record(self, name) -> str:
        try:
            self.data.pop(name)
            return f"{name} was removed"
        except KeyError:
            return "This user isn't in the Book"
        
    def get_contacts(self, file_name):
        with open(file_name, 'ab+') as fh:
            fh.seek(0)
            try:
                self.data = pickle.load(fh)
            except EOFError:
                pass   
        
    def iterator(self, n = 2):
        if len(self.data) > self.index:
            yield from [self.data[name] for name in sorted(self.data.keys())[self.index:self.index + n]]
            self.index += n
        else:
            raise StopIteration
            
    def show_records(self):
        batch = self.iterator()
        try:
            return "\n".join([record.show_record() for record in batch])
        except RuntimeError:
            self.index = 0
            return 'the end'
        
    def write_contacts(self, file_name) -> None:
        with open(file_name, "wb") as fh:
            pickle.dump(self, fh)
            

class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value


class Birthday(Field):
    format: str = None
    formats = ['%d/%m', '%d/%m/%Y', '%d-%m', '%d-%m-%Y']

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, birthday):  
        format = self.validate_date(birthday)
        if format != None:
            self.__value = birthday
            self.format = format
        else:
            raise ValueError(f"The birthday wasn't added, it should be in one of the formats: {', '.join([f for f in Birthday.formats])}")  

    def validate_date(self, date):
        for format in Birthday.formats:
            try:
                datetime.strptime(date, format)
                return format
            except ValueError:
                pass


class Name(Field):
    pass


class Phone(Field):   
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, phone):
        digits = sum([d.isdigit() for d in phone])
        match = re.match('^[+0-9-()]{7,18}$', phone)
        if digits < 7:
            raise ValueError("The number wasn't added. It should have at least 7 digits.")
        elif not match:
            raise ValueError("The number wasn't added. It can contain only the following characters: digits 0-9, '-', '(', ')', '+'.")
        self.__value = phone

class Record:
    def __init__(self, name: Name, phone: Phone=None, birthday: Birthday=None) -> None:
        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday

    def add_birthday(self, date: Birthday) -> None:
        self.birthday = date

    def add_phone(self, phone: Phone) -> None:
        self.phones.append(phone)

    def add_phones(self, phones: list[Phone]):
        if phones[0].value != '':
            self.phones.extend(phones)

    def days_to_birthday(self):
        if not self.birthday:
            return f"{self.name.value}'s birthday is unknown"
        date_bd = datetime.strptime(self.birthday.value, self.birthday.format)
        current_day = datetime.now()
        date_bd = datetime(year=current_day.year, month=date_bd.month, day=date_bd.day)
        difference = (date_bd - current_day).days
        if difference == 0:
            return f"{self.name.value}'s birthday is today!"
        elif difference < 0:
                difference = difference + 365 + calendar.isleap(current_day.year)
        return f"{self.birthday.value} It's {difference} days to {self.name.value}'s birthday."

    def delete_phone(self, pos: int = 0) -> None:
        if len(self.phones) > 1:
            pos = self.ask_index()
        try:
            self.phones.remove(self.phones[pos])
            return 'Done!'
        except:
            return pos

    def edit_phone(self, phone: Phone, pos: int = 0) -> str:    
            if len(self.phones) > 1:
                pos = self.ask_index()
            elif len(self.phones) == 0:
                self.phones.append(phone)
            try:
                self.phones[pos] = phone
                return 'Done!'
            except:
                return pos

    def show_record(self):
        return f"{self.name.value}: {', '.join([phone.value for phone in self.phones])} {self.birthday.value if self.birthday else ''}"
    
    def show_phone(self):
        return f"{self.name.value}: {', '.join([phone.value for phone in self.phones])}"

    def ask_index(self):
        print(self.name.value) 
        for i, number in enumerate([phone.value for phone in self.phones], 0): 
            print(f'{i}: {number}')
        while True: 
            try:        
                pos = int(input('Enter the index of a phone you want to edit >>> '))
                if pos > len(self.phones) - 1:
                    raise IndexError
                return pos
            except IndexError:
                return 'Wrong index. Try again.'
            except ValueError:
                return 'Index should be a number. Try again.'
            

class UserInterfaceAddressBook(UI):

    def __init__(self, contacts: AddressBook):
        self.contacts = contacts

    def decorator_input(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*words):
            try:
                return func(*words)
            except KeyError as err:
                return err
            except IndexError:
                return "You didn't enter the phone/birthday or a user"
            except TypeError:
                return "Sorry, this command doesn't exist"
            except Exception as err:
                return err
        return wrapper

    @decorator_input
    def add_birthday(self, *args: str) -> str:
        record = self.contacts.get(args[0])
        record.add_birthday(Birthday(args[1]))
        return 'Done!'

    @decorator_input
    def add_phone(self, *args: str) -> str:
        record = self.contacts.get(args[0])
        record.add_phone(Phone(args[1]))
        return 'Done!'

    @decorator_input
    def add_user(self, *args: str) -> str:
        name = Name(args[0])
        if name.value in self.contacts.keys():
            return "This user already exists."
        else:
            record = Record(name)
            mes = 'The user was added!'
            try:
                phone = Phone(args[1])
                record.add_phone(phone)
            except IndexError:
                phone = None
            except ValueError as err:
                mes = f'{mes} {err}'
            try:
                birthday = Birthday(args[2])
                record.add_birthday(birthday)
            except IndexError:
                birthday = None
            except ValueError as err:
                mes = f"{mes} {err}"  
            self.contacts.add_record(record)    
            return mes

    @decorator_input   
    def birthday(self, *args: str) -> str:
        record = self.contacts.get(args[0])
        return record.days_to_birthday()

    @decorator_input
    def change(self, *args: str) -> str:
        record = self.contacts.get(args[0])
        mes = record.edit_phone(Phone(args[1]))
        return mes

    @decorator_input
    def delete_phone(self, *args: str) -> str:
        record = self.contacts.get(args[0])
        mes = record.delete_phone()
        return mes

    @decorator_input
    def delete_user(self, *args: str) -> str:
        return self.contacts.delete_record(args[0])

    @decorator_input
    def hello(self) -> str:
        return 'How can I help you?'

    def display_help(self):
        return common.display_help()
    
    def get_command(self, words: str, commands_dict: dict) -> Callable:
        return common.get_command(words, commands_dict)
    
    def greeting(self):
        return "Welcome to Addressbook! If you need any help navigating the commands, write 'help'"
    
    def goodbye(self):
        return common.goodbye()

    @decorator_input
    def phone(self, *args: str) -> str:
        record = self.contacts[args[0]]
        return record.show_phone()

    @decorator_input
    def show(self, *args: str) -> str:
        found = []
        arg = re.sub('\+', '\\+', args[0])
        for record in self.contacts.values():
            match = re.search(arg, f"{record.name.value}|{'|'.join([phone.value for phone in record.phones])}")
            if match:
                found.append(record)
        if len(found) == 0:
            return "No matches"
        return "\n".join([record.show_record() for record in found])
    
    def showall(self):
        return self.contacts.show_records()


contacts = AddressBook()
ui = UserInterfaceAddressBook(contacts)

commands_dict = {('hello','hi', 'hey'):ui.hello,
                 ('add',):ui.add_user,
                 ('add_birthday',): ui.add_birthday,
                 ('add_phone',):ui.add_phone,
                 ('birthday',): ui.birthday,
                 ('help',): ui.display_help,
                 ('show',): ui.show,
                 ('change',):ui.change,
                 ('delete_phone',):ui.delete_phone,
                 ('delete',):ui.delete_user,
                 ('phone',):ui.phone,
                 ('showall',):ui.showall,
                 ('goodbye','close','exit','quit'):ui.goodbye
}

commands_description = [['add', "Add a user", 'add <User name>'],
                        ['add_birthday', "Add existing user's birthday", 'add_birthday <User name> <birthday>'],
                        ['add_phone', "Add existing user's phone number", 'add_phone <User name> <number>'],
                        ['birthday', "Display user's birthday", 'birthday <User name>'],
                        ['change', "Edit user's phone", 'change <User name>'],
                        ['Delete', "Delete user", 'delete <User name>'],
                        ['Delete_phone', "Delete user's phone number", 'delete_phone <User name>'],
                        ['goodbye/close/exit/quit', "Any of these commands will exit the app", 'quit'],
                        ['help', "Get help", 'help'],
                        ['hello/hi/hey', "Greet the Addressbook", 'hi'],
                        ['phone', "Display user's phone number", 'phone <User name>'],
                        ['show', "Display existing user's info", 'show <User name>'],
                        ['showall', "Dislplay all users' info", 'showall']
                            
    ]

commands_list = [cmd for cmds in commands_dict.keys() for cmd in cmds]
word_completer = WordCompleter(commands_list)

def main():
    colorit.init_colorit()
    print(ui.greeting())
    contacts.get_contacts('contacts.bin')
    while True:
        words = prompt("Your command >>> ", completer = word_completer).split(' ')
        try:
            func = ui.get_command(words, commands_dict)
        except KeyError as error:
            print(error)
            continue
        print(func(*words[1:])) 
        if func.__name__ == 'goodbye':
            contacts.write_contacts('contacts.bin')
            break

if __name__ == '__main__':
    main()
    