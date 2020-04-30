import kivy
kivy.require('1.11.1') # Kivy version

from kivy.config import Config
# By default kivy exits when Esc is pressed, overwrite it
Config.set('kivy', 'exit_on_escape', '0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.rst import RstDocument
from kivy.clock import Clock
from kivy.uix.slider import Slider
from kivy.uix.dropdown import DropDown
from kivy.uix.modalview import ModalView

# For online sync
from git import Repo
import datetime
import socket

# Filesystem
import os

# Markdown to restructuredText
from m2r import convert

# Used for natural sorting
import re 

# For audio playing
from pygame import mixer

# For text indexing
from whoosh import index
from whoosh.fields import Schema, ID, TEXT
from whoosh.qparser import MultifieldParser

# Global definitions
# This is the path where notes will be stored and read from
hobbes_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')

'''
    TODO:

        - Fix images/attachments relative paths, that can be done when converting Markdown -> reStructuredText
        - Add option to export to pdf
        - Add git
        - Implement contextual menu options
'''

'''
    From the Whoosh docs, incremental indexing of the files
'''
def index_my_docs(db_path, dirname, clean=False):

    # If the index folder does not exist create it
    if not os.path.exists(os.path.join(db_path, dirname)):

        os.mkdir(os.path.join(db_path, dirname))

    if clean:

        clean_index(db_path, dirname)
    else:

        incremental_index(db_path, dirname)

def clean_index(db_path, dirname):
    # Always create the index from scratch
    ix = index.create_in(os.path.join(db_path, dirname), schema=get_schema())
    writer = ix.writer()

    # Assume we have a function that gathers the filenames of the
    # documents to be indexed
    for path in my_docs(db_path):
        add_doc(writer, path)

    writer.commit()

def my_docs(db_path):

    # Get all the txt files from a given path
    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(db_path) for f in filenames if os.path.splitext(f)[1] == '.txt']
    return result

def get_schema():

    return Schema(path=ID(unique=True, stored=True), title=TEXT(stored=True), content=TEXT)

def add_doc(writer, path):

    fileobj = open(path, "rb")
    content = fileobj.read()
    fileobj.close()
    title = os.path.basename(path).split(".")[0]
    writer.add_document(path=path, content=content.decode("utf-8", "strict"), title=title)

def incremental_index(db_path, dirname):

    ix = index.open_dir(os.path.join(db_path, dirname))

    # The set of all paths in the index
    indexed_paths = set()

    # The set of all paths we need to re-index
    to_index = set()

    with ix.searcher() as searcher:
        writer = ix.writer()

        # Loop over the stored fields in the index
        for fields in searcher.all_stored_fields():
            indexed_path = fields['path']
            indexed_paths.add(indexed_path)

        if not os.path.exists(indexed_path):
            # This file was deleted since it was indexed
            writer.delete_by_term('path', indexed_path)

        else:
            # Check if this file was changed since it
            # was indexed
            indexed_time = fields['time']
            mtime = os.path.getmtime(indexed_path)

            if mtime > indexed_time:
                # The file has changed, delete it and add it to the list of
                # files to reindex
                writer.delete_by_term('path', indexed_path)
                to_index.add(indexed_path)

        # Loop over the files in the filesystem
        # Assume we have a function that gathers the filenames of the
        # documents to be indexed
        for path in my_docs(db_path):
            if path in to_index or path not in indexed_paths:
                # This is either a file that's changed, or a new file
                # that wasn't indexed before. So index it!
                add_doc(writer, path)

        writer.commit()

'''
    Search popup
'''
class SearchPopup(ModalView):

    def __init__(self, **kwargs):

        super(SearchPopup, self).__init__(**kwargs)

        self.background = 'media/images/transparent.png'
        self.background_color = (0, 0, 0, 0)

        self.pos_hint = {'top': 0.9}

        self.layout = BoxLayout(orientation='vertical', size_hint=(1, None))

        self.layout.bind(minimum_height = self.setter('height'))


        self.textinput = TextInput(text='', multiline=False, size_hint=(1, None), size=(0, 30))
        self.layout.add_widget(self.textinput)

        self.add_widget(self.layout)

        self.textinput.bind(on_text_validate=self.do_search)

        self.buttons = []


    def clear_all(self):

        self.textinput.text=''
        self.clear_results()

    def clear_results(self):

        for btn in self.buttons:

            self.layout.remove_widget(btn)

    def do_search(self, textinput):

        self.clear_results()

        print("Searching")

        print(self.layout.size)

        # Create the searcher
        ix = index.open_dir(os.path.join(hobbes_db, '.text_index'))

        with ix.searcher() as searcher:

            parser = MultifieldParser(["title", "content"], schema=ix.schema)

            query = parser.parse(textinput.text)
            results = searcher.search(query, terms=True)

            for hit in results:

                btn = Button(text=hit['title'], size_hint=(1, None), size=(0, 30))
                self.layout.add_widget(btn)

                self.buttons.append(btn)

                print(hit)
                print(hit.matched_terms())

        #self.pos_hint = {'top': 0.1}

        # Keep the focus on the textinput
        self.textinput.focus = True

        print(self.layout.size)


    # Set the focus when opened
    def on_open(self):

        self.textinput.focus = True


""" Sort the given iterable in the way that humans expect.""" 
def sorted_nicely(l): 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key=alphanum_key)


'''
    Generic info popup
'''

class InfoPopup(Popup):

    def __init__(self, message, **kwargs):

        super(InfoPopup, self).__init__(**kwargs)

        self.add_widget(Label(text=message))

'''
    Generic textinput popup
'''
class TextinputPopup(Popup):

    def __init__(self, message, callback, **kwargs):

        super(TextinputPopup, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        layout.add_widget(Label(text=message, size_hint=(1, .5)), 1)
        self.textinput = TextInput(text='', multiline=False, size_hint=(1, .5))

        layout.add_widget(self.textinput, 0)

        self.add_widget(layout)

        self.textinput.bind(on_text_validate=self.my_callback)

        self.callback = callback

    def my_callback(self, textinput):

        self.callback(self, textinput.text)

    # Set the focus when opened
    def on_open(self):

        self.textinput.focus = True

'''
    Generic confirmation dialog
'''
class ConfirmPopup(Popup):

    def __init__(self, message, callback, **kwargs):

        super(ConfirmPopup, self).__init__(**kwargs)

        layout_top = BoxLayout(orientation='vertical', size_hint=(1, .5))
        layout_top.add_widget(Label(text=message, size_hint=(1, .5)), 1)

        layout_bottom = BoxLayout(orientation='horizontal', size_hint=(1, .5))

        self.confirm_button = Button(text='Confirm', size_hint=(.5, 1))
        layout_bottom.add_widget(self.confirm_button)
        self.cancel_button = Button(text='Cancel', size_hint=(.5, 1))
        layout_bottom.add_widget(self.cancel_button)
        layout_top.add_widget(layout_bottom)

        self.add_widget(layout_top)

        # If the cancel button is pressed, just close the popup
        self.confirm_button.bind(on_release=self.my_callback)
        self.cancel_button.bind(on_release=self.dismiss)

        self.callback = callback

    def my_callback(self, l):

        self.callback(self)

    # Set the focus when opened
    def on_open(self):

        self.confirm_button.focus = True

'''
    Contextual menu for the folder view
'''
class FolderTreeViewContextMenu(Popup):

    def __init__(self, **kwargs):
        super(FolderTreeViewContextMenu, self).__init__(**kwargs)

        self.title = "Menu"

        self.context_menu = BoxLayout(orientation='vertical')

        # Create the options
        new_note_button   = Button(text="New note")
        new_folder_button = Button(text="New folder")
        rename_folder_button = Button(text="Rename folder")
        new_root_folder_button = Button(text="New root folder")

        # Special dialogues are needed for the following options
        move_folder_button     = Button(text="Move folder")
        export_folder_button   = Button(text="Export folder to PDF")
        delete_folder_button   = Button(text="Delete folder")

        self.context_menu.add_widget(new_note_button)
        self.context_menu.add_widget(new_folder_button)
        self.context_menu.add_widget(rename_folder_button)
        self.context_menu.add_widget(new_root_folder_button)
        self.context_menu.add_widget(move_folder_button)
        self.context_menu.add_widget(export_folder_button)
        self.context_menu.add_widget(delete_folder_button)

        # Bind the buttons to functions
        new_note_button.bind(on_release = self.create_note_popup) 
        new_folder_button.bind(on_release = self.create_folder_popup)
        rename_folder_button.bind(on_release = self.rename_folder_popup)
        new_root_folder_button.bind(on_release = self.create_root_folder_popup)

        move_folder_button.bind(on_release = self.move_folder_popup)
        export_folder_button.bind(on_release = self.export_folder_popup)
        delete_folder_button.bind(on_release = self.delete_folder_popup)

        self.content = self.context_menu

        self.current_folder = None

    # When the menu is opened the current folder pointer is stored
    def menu_opened(self, folder):

        self.current_folder = folder
        self.open()

    '''
        Functions that create textinput popups for the actions
    '''
    def create_note_popup(self, *l):

        if self.current_folder != None:

            self.dismiss()

            info = TextinputPopup(title="New note", message="Insert note name", callback=self.create_note, size_hint=(.2, .2))
            info.open()

    def create_folder_popup(self, *l):

        if self.current_folder != None:
            self.dismiss()

            info = TextinputPopup(title="New folder", message="Insert folder name", callback=self.create_folder, size_hint=(.2, .2))
            info.open()

    def rename_folder_popup(self, *l):

        if self.current_folder != None:
            self.dismiss()

            info = TextinputPopup(title="Rename folder", message="Insert folder name for folder '%s'" % self.current_folder.text, callback=self.rename_folder, size_hint=(.2, .2))
            info.open()

    def create_root_folder_popup(self, *l):

        self.dismiss()
        info = TextinputPopup(title="New root folder", message="Insert root folder name", callback=self.create_root_folder, size_hint=(.3, .2))
        info.open()

    '''
        Functions that require custom dialogues
    '''
    def move_folder_popup(self, *l):

        self.dismiss()

        # If the user clicks on another folder, the folder moves there

    def export_folder_popup(self, *l):

        self.dismiss()

        # Open filesystem to get new path

        # Recursively convert notes to PDF

    def delete_folder_popup(self, *l):

        self.dismiss()

        # Need confirmation
        confirm = ConfirmPopup(title="Delete folder", message="Are you sure you want to delete folder '%s'?" % self.current_folder.text, callback=self.delete_folder, size_hint=(.2, .2))
        confirm.open()


    '''
        Functions that actually do things
    '''

    def create_note(self, popup, text):

        print("Creating note", text, " on folder ", self.current_folder.text)
        popup.dismiss()

    def create_folder(self, popup, text):

        print("Creating folder", text, " on folder ", self.current_folder.text)
        popup.dismiss()


    def create_root_folder(self, popup, text):

        print("Creating root folder", text)
        popup.dismiss()

    def rename_folder(self, popup, text):

        print("Renaming folder %s to %s" % (self.current_folder.text, text))
        popup.dismiss()

    def move_folder(self, popup):

        if self.current_folder != None:

            print("Moving folder", self.current_folder.text)
            popup.dismiss()

    def export_folder(self, popup):

        if self.current_folder != None:

            print("Exporting folder", self.current_folder.text)
            popup.dismiss()

    def delete_folder(self, popup):

        if self.current_folder != None:

            print("Deleting folder", self.current_folder.text)
            popup.dismiss()

'''
    Contextual menu for the note view
'''
class NoteViewContextMenu(Popup):

    def __init__(self, **kwargs):
        super(NoteViewContextMenu, self).__init__(**kwargs)

        self.title = "Menu"

        self.context_menu = BoxLayout(orientation='vertical')

        # Create the options
        rename_note_button   = Button(text="Rename note")
        move_note_button     = Button(text="Move note")
        delete_note_button   = Button(text="Delete note")
        export_note_button   = Button(text="Export note to PDF")
        self.context_menu.add_widget(rename_note_button)
        self.context_menu.add_widget(move_note_button)
        self.context_menu.add_widget(delete_note_button)
        self.context_menu.add_widget(export_note_button)

        # Bind the buttons to functions
        rename_note_button.bind(on_release = self.rename_note_popup) 
        move_note_button.bind(on_release = self.move_note_popup)
        delete_note_button.bind(on_release = self.delete_note_popup)
        export_note_button.bind(on_release = self.export_note_popup)

        self.content = self.context_menu

        self.current_note = None

    def menu_opened(self, note):

        self.current_note = note
        self.open()

    '''
        Popup functions
    '''
    def rename_note_popup(self, *l):

        if self.current_note != None:
            self.dismiss()

            info = TextinputPopup(title="Rename note", message="Insert folder name for note '%s'" % self.current_note.text, callback=self.rename_note, size_hint=(.2, .2))
            info.open()


    def move_note_popup(self, *l):

        if self.current_note != None:
            self.dismiss()

    def delete_note_popup(self, *l):

        if self.current_note != None:
            self.dismiss()

            # Need confirmation
            confirm = ConfirmPopup(title="Delete note", message="Are you sure you want to delete note '%s'?" % self.current_note.text, callback=self.delete_note, size_hint=(.2, .2))
            confirm.open()

    def export_note_popup(self, *l):

        if self.current_note != None:
            self.dismiss()

    def rename_note(self, *l):

        if self.current_note != None:

            print("Rename note", self.current_note.text)

    def move_note(self, *l):

        if self.current_note != None:

            print("Move note", self.current_note.text)

    def delete_note(self, *l):

        if self.current_note != None:

            print("Delete note", self.current_note.text)

    def import_note_to_pdf(self, in_path, out_path):

        # This imports are expensive, that is why they are not loaded on start
        from markdown import markdown
        from weasyprint import HTML

        html = markdown(self.note_text_input.text, output_format='html4')

        html = HTML(string=html)
        html.write_pdf('/tmp/example.pdf')

'''
    This represents a folder on the treeview
'''
class FolderLabel(TreeViewLabel):

    # I'm storing here the filesystem path of the folder
    path = ''

    def __init__(self, path='', **kwargs):
        super(FolderLabel, self).__init__(**kwargs)

        self.path = path

'''
    This function traverses a directory and adds the folders as children to
    the given tree
'''
def populate_tree(tree, path):

    added = []

    # Helper functions used to sort
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 

    for root, dirs, files in os.walk(path):

        # Remove directories starting by .
        dirs[:] = [d for d in dirs if not d[0] == '.']

        # Alfabetical order
        dirs.sort(key=alphanum_key)

        level = root.replace(path, '').count(os.sep)

        # Ignore the same folder

        if root == path:
            continue

        # Add the rest of folders recursively
        if level == 1:

            added = []
            added.append(tree.add_node(FolderLabel(text=os.path.basename(root), path=root)))
        else:

            added.append(tree.add_node(FolderLabel(text=os.path.basename(root), path=root), added[level-2]))

'''
    This is a custom Tree View to view the folders
'''
class FolderTreeView(TreeView):

    def __init__(self, notes_view,  **kwargs):
        super(FolderTreeView, self).__init__(**kwargs)

        self.hide_root=True
        self.bind(minimum_height = self.setter('height'))

        self.notes_view = notes_view

        populate_tree(self, hobbes_db)

        # Context menu
        self.context_menu = FolderTreeViewContextMenu(size_hint=(.2, .2))

    def custom_event_handler(self, touch):

        if touch.button != 'scrolldown' and touch.button != 'scrollup':

            active_node = self.get_node_at_pos((touch.x, touch.y))
            
            if active_node != None:

                self.notes_view.add_notes(active_node.path)

                if touch.button == 'right' or touch.is_double_tap:

                    self.context_menu.menu_opened(active_node)

                    return True

            # There is no node under the cursor
            else:

                print("Not a leaf")

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

    def __init__(self, note_text_panel, **kwargs):

        self.active_note = None
        self.note_text_panel = note_text_panel

        super(NoteView, self).__init__(**kwargs)

        self.bind(minimum_height = self.setter('height'))

        # Context menu
        self.context_menu = NoteViewContextMenu(size_hint=(.2, .2))

    def add_notes(self, path):

        self.clear_widgets()

        for file in sorted_nicely(os.listdir(path)):
            if file.endswith(".txt"):

                self.add_widget(NoteButton(context_menu=self.context_menu, note_view=self, text=file.split(".")[0], path=os.path.join(path, file), size_hint=(1, None), size=(0, 20), text_size=(self.width, None), halign='left'))

    '''
        This function handles when a note has been activated
    '''
    def activate_note(self, note):

        # Background logic
        if self.active_note != None:

            self.active_note.background_color = (1, 1, 1, 1) # Background color of note

        note.background_color  = (1, 1, 1, 0.5) # Background color when selected
        self.active_note = note

        # Send note to text input
        self.note_text_panel.load_note(self.active_note.path)


'''
    This will be used to edit notes
'''
class NoteTextInput(TextInput):

    def __init__(self, **kwargs):
        super(NoteTextInput, self).__init__(**kwargs)

        self.font_size = 24
        self.background_normal = ''
        self.padding = [16, 15, 6, 6]

class NoteTextRenderer(RstDocument):

    def __init__(self, **kwargs):
        super(NoteTextRenderer, self).__init__(**kwargs)

        # Available colors
        #{'background': 'ffffffff', 'link': 'ce5c00ff', 'paragraph': '202020ff', 'title': '204a87ff', 'bullet': '000000ff'}

        # Set the background color to white
        self.background_color = (1, 1, 1, 1)

        #  Set the color of the underline of the titles
        self.underline_color = '000000FF'

        # Set the size of the title, the rest of the font sizes are derived from this
        self.base_font_size = 48

'''
    Combination of the text editor and renderer, I  write my notes in Markdown but the renderer is in reStructuredText
'''
class NoteTextPanel(BoxLayout):

        note_text_input    = NoteTextInput(size_hint=(.5, 1), multiline=True)
        note_text_renderer = NoteTextRenderer(size_hint=(.5, 1))

        current_note = None

        # Possible view status: 0 = split, 1 = Note, 2 = renderer
        toggle_status = 0

        def __init__(self, **kwargs):
            super(NoteTextPanel, self).__init__(**kwargs)

            self.orientation = 'horizontal'
            self.add_widget(self.note_text_input)

            # Listen to input text and render it realtime
            self.note_text_input.bind(text=self.on_input_text)

            self.add_widget(self.note_text_renderer)

            # Autosave each 30 seconds
            Clock.schedule_interval(self.autosave, 30)

        def on_input_text(self, instance, text):

            self.note_text_renderer.text = convert(text)

        # Toggle between split view, text or renderer
        def toggle(self):

            self.toggle_status = (self.toggle_status + 1) % 3

            if self.toggle_status == 0:

                self.add_widget(self.note_text_input, 1)
                self.note_text_input.disabled = False

            elif self.toggle_status == 1:

                self.remove_widget(self.note_text_renderer)

            else:

                self.remove_widget(self.note_text_input)
                self.add_widget(self.note_text_renderer)
                self.note_text_input.disabled = True

        # Displays a note on the editor
        def load_note(self, path):

            if self.current_note == None:

                self.current_note = path
            else:

                # Save previous note if any
                self.save_note()

            print("Load: ", path)

            # Store the current path
            self.current_note = path

            # Open note
            with open(path, 'r') as note:
                text = note.read()

            self.note_text_input.text = text

        # Saves the contents of the current editor to the current note
        def save_note(self):

            if self.current_note != None:

                print("Writting", self.note_text_input.text, " to", self.current_note)

                with open(self.current_note, 'w') as note:
                    note.write(self.note_text_input.text)

        # Autosave function
        def autosave(self, dt):

            self.save_note()

class MusicSlider(Slider):

    def __init__(self, **kwargs):
        super(MusicSlider, self).__init__(**kwargs)

        # Audio
        mixer.init()
        mixer.set_num_channels(1)
        self.rain = mixer.Sound("media/audio/rain.ogg")

    def on_touch_up(self, touch):

        if self.value > 0:

            # If the sound is not playing, start it
            if not mixer.get_busy():

                self.rain.play(loops=-1)

            self.rain.set_volume(self.value)

        else:

            self.rain.fadeout(2000)    

        return True

'''
    This is the Layout of the main screen of the application
'''
class MainScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Orientation of the Box Layouts
        self.orientation='horizontal'

        # Notes input panel
        self.note_text_input = NoteTextPanel(size_hint=(.6, 1))

        # Notes view
        self.notes_view_scroll = ScrollView(size_hint=(.2, None))
        self.notes_view = NoteView(note_text_panel=self.note_text_input, cols=1, size_hint=(1, None))
        self.notes_view_scroll.add_widget(self.notes_view, 0)

        # Folders view
        self.folder_tree_view_scroll = ScrollView(size_hint=(1, 1))
        self.folder_tree_view = FolderTreeView(size_hint_y=None, notes_view=self.notes_view)
        self.folder_tree_view_scroll.add_widget(self.folder_tree_view, 1)

        # Add the tiny slider for the rain
        audio_layout = BoxLayout(orientation='vertical', size_hint=(.2, 1))
        audio_layout.add_widget(self.folder_tree_view_scroll)
        self.slider = MusicSlider(min=0, max=1, value=0, step=0.05, cursor_size=(15, 15), cursor_image='media/images/slider.png', background_width='18sp', size_hint=(1, 0.1))
        audio_layout.add_widget(self.slider)

        # Add the audio layout
        self.add_widget(audio_layout)
        self.add_widget(self.notes_view_scroll)
        self.add_widget(self.note_text_input)

        # Pay attention to keyboard events
        Window.bind(on_key_down=self.on_keyboard)

        # Search popup
        self.search_popup = SearchPopup(size_hint=(None, None), size=(400, 0))


        '''
        GIT TEST: Better do this in a new thread
        '''

        ## Check if the .git folder exist on the repo
        #repo = Repo(os.path.join(hobbes_db, 'Work'))
        #origin = repo.remote(name='origin')

        ## Pull any changes
        #origin.pull()

        ## Add new changes
        #repo.git.add('--all')
        #date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #device_name = socket.gethostname()
        #repo.index.commit('Sync: ' + date + ' Device: ' + device_name)
        #
        ## Push everything
        #origin.push()

        '''
            Indexing test
        '''
        index_my_docs(hobbes_db, '.text_index', True)


    # This method will be in charge of all the input actions
    def on_touch_down(self, touch):

        # Handle TreeView touch
        if self.folder_tree_view_scroll.collide_point(touch.x, touch.y):

            print("On tree")

            # Save the touch since we are making coordinates transform
            touch.push()

            # We need to fix the coordinate system since the scroll has moved the widget
            touch.apply_transform_2d(self.folder_tree_view_scroll.to_local)
            self.folder_tree_view.custom_event_handler(touch)

            # Restore touch
            touch.pop()

        return super(MainScreen, self).on_touch_down(touch)

    # React to key combinations
    def on_keyboard(self, window, key, scancode, codepoint, modifier):

        if 'ctrl' in modifier and codepoint == 'l':

            self.note_text_input.toggle()

        elif 'ctrl' in modifier and codepoint == 's':

            self.note_text_input.save_note()

        elif 'ctrl' in modifier and codepoint == 'g':

            #s = SearchPopup(size_hint=(.8, None))
            #s.open()
            self.search_popup.clear_all()
            self.search_popup.open()


class HobbesApp(App):

    def build(self):
        return MainScreen()

if __name__ == '__main__':
    HobbesApp().run()