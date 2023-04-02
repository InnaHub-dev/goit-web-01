import functools
import os
import pickle
import re
import subprocess
from collections import UserDict
from typing import Callable

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt

from . import common
from .abstract_ui import UI


class MyException(Exception):
    pass

class NotePad(UserDict):
    def __getitem__(self, title):
        if not title in self.data.keys():
            raise MyException("This article isn't in the Notepad")
        note = self.data[title]
        return note
    
    def add_note(self, note) -> str:
        self.data.update({note.title.value:note})
        return 'Done!'

    def delete_note(self, title):
        try:
            self.data.pop(title)
            return f"{title} was removed"
        except KeyError:
            return "This note isn't in the Notepad"
         
    def get_notes(self, file_name):
        with open(file_name, 'ab+') as fh:
            fh.seek(0)
            try:
                self.data = pickle.load(fh)
            except EOFError:
                pass 

    def show_notes_titles(self):
        return "\n".join([note for note in notes])
    
    def write_notes(self, file_name):
        with open(file_name, "wb") as fh:
            pickle.dump(self, fh)


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value


class NoteTag(Field):
    pass


class NoteTitle(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, title):
        if len(title) == 0:
            raise ValueError("The title wasn't added. It should have at least 1 character.")
        self.__value = title


class NoteBody(Field):
    pass


class Note:
    def __init__(self, title: NoteTitle, body: NoteBody, tags: list[NoteTag]=None) -> None:
        self.title = title
        self.body = body if body else ''
        self.tags = tags if tags else ''

    def edit_tags(self, tags: list[NoteTag]):
        self.tags = tags

    def edit_title(self, title: NoteTitle):
        self.title = title

    def edit_body(self, body: NoteBody):
        self.body = body

    def show_note(self):
        title = f"Title: {self.title.value}"
        body = f"Body: {self.body.value}" # add write the limitations for the width of the note
        tags = f"Tags: {self.show_tags()}"
        return '\n'.join([title, body, tags])
    
    def show_tags(self):
        if self.tags == []:
            return ""
        return ', '.join([tag.value for tag in self.tags])

class UserInterfaceNotepad(UI):
    def decorator_input(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*words):
            try:
                return func(*words)
            except KeyError as err:
                return err
            except IndexError:
                return "You didn't enter the title or keywords"
            except TypeError:
                return "Sorry, this command doesn't exist"
            except Exception as err:
                return err
        return wrapper

    @decorator_input
    def add_note(*args) -> str:
        title = NoteTitle(input("Enter the title: "))
        if title.value in notes.data.keys():
            raise MyException('This title already exists')
        body = NoteBody(input("Enter the note: "))
        tags = input("Enter tags (separate them with ',') or press Enter to skip this step: ")
        tags = [NoteTag(t.strip()) for t in tags.split(',')]
        note = Note(title, body, tags)
        return notes.add_note(note)

    @decorator_input
    def delete_note(*args: str) -> str:
        return notes.delete_note(args[0])
    
    def display_help(self):
        return common.display_help(commands_description)

    @decorator_input
    def edit(self, text: str, part) -> str:
        user_input = input(f"Enter any letter if you want to edit {part} or press 'enter' to skip this step. ")
        if user_input:
            with open('edit_note.txt', 'w') as fh:
                fh.write(text)
            self.run_app()
            mes = ''
            if part == 'tags':
                mes = "Separate tags with ',' "
            input(f'Press Enter or any letter if you have finished editing. Please, make sure you closed the text editor. {mes}')
            with open('edit_note.txt', 'r') as fh:
                edited_text = fh.read()
            return edited_text

    def edit_body(self, note: Note) -> str:
        body = self.edit(note.body.value, 'body')
        if body:
            body = NoteBody(body)
            note.edit_body(body)

    @decorator_input        
    def edit_note(self, *args) -> str:
        title = args[0]
        note = notes.data.get(title)
        self.edit_title(title, note)
        self.edit_body(note)
        self.edit_tags(note)
        return "Done!"

    def edit_tags(self, note: Note) -> str:
        tags = self.edit(note.show_tags(), 'tags')
        if tags:
            tags = [NoteTag(t.strip()) for t in tags.split(',')]
            note.edit_tags(tags)
    
    def edit_title(self, title: str, note: Note) -> str:
        user_title = input("Enter new title or press 'enter' to skip this step: ")
        if user_title:
            if not user_title in notes.data.keys():
                notes.data[user_title] = notes.data.pop(title)
                note.edit_title(NoteTitle(user_title))
            else:
                raise MyException('This title already exists.')
        
    @decorator_input  
    def find(self, *args) -> str:
        #add avoiding special characters \ + etc.
        searched_phrase = ' '.join([arg for arg in args])
        expression = re.compile(searched_phrase, flags=re.IGNORECASE)
        found_notes = []
        for note in notes.data.values():
            if expression.search(note.body.value) or expression.search(note.title.value):
                found_notes.append(note.title.value)
        found_notes_str = '\n'.join([title for title in found_notes])
        return f"Found {len(found_notes)} article(s) with '{searched_phrase}': \n{found_notes_str}"
        
    @decorator_input  
    def find_tags(self, *args: str) -> str:
        if len(args) == 0:
            return "You didn't enter any tags."
        all_notes = [note for note in notes.data.values()]
        notes_dict = {}
        arg_set = set(args)
        for note in all_notes:
            matches = arg_set.intersection(set(tag.value for tag in note.tags))
            if matches:
                notes_dict[note.title.value] = ', '.join(matches)
        sorted_dict = sorted(notes_dict, key=lambda k: len(notes_dict[k]), reverse=True)
        return '\n'.join([f"{key}: {notes_dict[key]}" for key in sorted_dict])

    def goodbye(self):
        return common.goodbye()

    def greeting(self):
        return "Welcome to the Notepad assistant! If you need any help navigating the commands, write 'help'"

    @decorator_input  
    def run_app(self):
        if os.name == "nt":  # For Windows
            os.startfile('edit_note.txt')
        else:  # For Mac
            subprocess.call(["open", 'edit_note.txt'])

    @decorator_input
    def show_note(self, *args:str) -> str:
        note = notes.data.get(args[0])
        return note.show_note()

notes = NotePad()
ui = UserInterfaceNotepad()

commands_dict = {('add', 'add_note'):ui.add_note,
                 ('edit', 'edit_note'):ui.edit_note,
                 ('help',):ui.display_help,
                 ('show', 'show_note'):ui.show_note,
                 ('showall',):notes.show_notes_titles,
                 ('find_tags',):ui.find_tags,
                 ('find',):ui.find,
                 ('delete',):ui.delete_note,
                 ('goodbye','close','exit','quit'):ui.goodbye
}

commands_description = [['add/add_note', "Any of these commands will add a new note to a Notepad", 'add/add_note <Note name>'],
                        ['edit/edit_note', "Any of these commands will edit a note", 'edit/edit_note <Note name>'],
                        ['show/show_note', "Any of these commands will display a note", 'show/show_note <Note name>'],
                        ['showall', "Dislplay all notes' names", 'showall'],
                        ['find_tags', "Display all the articles with the tag/tags", 'find_tags <tag1> <tag2> ... <tag n>'],
                        ['find', "Display all the notes containing the search query in their body/title", 'find <text>'],
                        ['delete', "Delete existing note from the Notepad", 'delete <Note name>'],
                        ['goodbye/close/exit/quit', "Any of these commands will exit the app", 'goodbye/close/exit/quit']
]

commands_list = [cmd for cmds in commands_dict.keys() for cmd in cmds]
word_completer = WordCompleter(commands_list)

def main():

    print(ui.greeting())
    notes.get_notes('notes.bin')

    while True:
        words = prompt("Your command >>>  ", completer = word_completer).split(' ')
        try:
            func = common.get_command(words, commands_dict)
        except KeyError as error:
            print(error)
            continue
        print(func(*words[1:])) 
        if func.__name__ == 'goodbye':
            notes.write_notes('notes.bin')
            break

if __name__ == '__main__':
    main()



