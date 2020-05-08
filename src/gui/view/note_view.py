from src.gui.context_menu.note_context_menu import *
from kivy.uix.gridlayout import GridLayout
import os
import re

NOTE_VIEW_NOT_ACTIVE_NOTE_COLOR = (1, 1, 1, 1)
NOTE_VIEW_ACTIVE_NOTE_COLOR = (1, 1, 1, 0.5)

""" Sort the given iterable in the way that humans expect.""" 
def sorted_nicely(l): 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key=alphanum_key)

'''
    Each of the notes is represented by one button
'''
class NoteButton(Button):

    def __init__(self, context_menu, note_view, path,  **kwargs):
        super(NoteButton, self).__init__(**kwargs)

        self.context_menu = context_menu
        self.note_view = note_view
        self.path = path
        
    def on_touch_down(self, touch):

        if self.collide_point(touch.x, touch.y):

            print("I have been touched ", self.text)

            self.note_view.activate_note(self)

            if touch.button == 'right' or touch.is_double_tap:

                self.context_menu.menu_opened(self)

            return super(NoteButton, self).on_touch_down(touch)

'''
    This is the column that shows notes
'''
class NoteView(GridLayout):

    # Store the note path to use with the search function
    path_dictionary = {}

    def __init__(self, note_text_panel, **kwargs):

        self.active_note = None
        self.note_text_panel = note_text_panel

        super(NoteView, self).__init__(**kwargs)

        self.bind(minimum_height = self.setter('height'))

        # Context menu
        self.context_menu = NoteViewContextMenu(size_hint=(.2, .3))

    def add_notes(self, path):

        self.clear_widgets()
        self.path_dictionary = {}

        for file in sorted_nicely(os.listdir(path)):
            if file.endswith(".md"):

                nb = NoteButton(context_menu=self.context_menu, note_view=self, text=file.split(".")[0], path=os.path.join(path, file), size_hint=(1, None), size=(0, 20), text_size=(self.width, None), halign='left')
                self.add_widget(nb)

                self.path_dictionary[os.path.join(path, file)] = nb

    '''
        This function handles when a note has been activated
    '''
    def activate_note(self, note):

        # Background logic
        if self.active_note != None:

            self.active_note.background_color = NOTE_VIEW_NOT_ACTIVE_NOTE_COLOR # Background color of note

        note.background_color  = NOTE_VIEW_ACTIVE_NOTE_COLOR # Background color when selected
        self.active_note = note

        # Send note to text input
        self.note_text_panel.load_note(self.active_note.path)
