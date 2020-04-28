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

# Filesystem
import os

# Markdown to restructuredText
from m2r import convert

# Used for natural sorting
import re 

# For audio playing
from pygame import mixer


'''
    TODO:

        - Fix images/attachments relative paths, that can be done when converting Markdown -> reStructuredText
        - Add option to export to pdf
        - Add rain sound
        - Add git
        - Finish contextual menu options

            (Tree context menu)
            - Rename folder
            - Create folder
            - Create note
            - Delete folder
            - Move folder
            - Export folder to pdf

            (Note context menu)
            - Rename note
            - Delete note
            - Create note
            - Export note to pdf
'''


def sorted_nicely(l): 
    """ Sort the given iterable in the way that humans expect.""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key=alphanum_key)

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
        self.context_menu.add_widget(new_note_button)
        self.context_menu.add_widget(new_folder_button)

        # Bind the buttons to functions
        new_note_button.bind(on_release = self.create_note) 
        new_folder_button.bind(on_release = self.create_folder)

        self.content = self.context_menu

        self.current_folder = None

    def menu_opened(self, folder):

        self.current_folder = folder
        self.open()


    def create_note(self, *l):

        if self.current_folder != None:

            print("Creating note on folder ", self.current_folder.text)

    def create_folder(self, *l):

        if self.current_folder != None:

            print("Creating folder on folder ", self.current_folder.text)

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
        self.context_menu.add_widget(rename_note_button)
        self.context_menu.add_widget(move_note_button)
        self.context_menu.add_widget(delete_note_button)

        # Bind the buttons to functions
        rename_note_button.bind(on_release = self.rename_note) 
        move_note_button.bind(on_release = self.move_note)
        delete_note_button.bind(on_release = self.delete_note)

        self.content = self.context_menu

        self.current_note = None

    def menu_opened(self, note):

        self.current_note = note
        self.open()

    def rename_note(self, *l):

        if self.current_note != None:

            print("Rename note", self.current_note.text)

    def move_note(self, *l):

        if self.current_note != None:

            print("Move note", self.current_note.text)

    def delete_note(self, *l):

        if self.current_note != None:

            print("Delete note", self.current_note.text)

    def import_note_to_pdf(self, path):

        # import Markdown to pdf, it is too slow to de everytime
        from markdown import markdown
        from weasyprint import HTML

        html = markdown(self.note_text_input.text, output_format='html4')

        html = HTML(string=html)
        html.write_pdf('/tmp/example.pdf')

'''
    This represents a folder on the treeview
'''
class FolderLabel(TreeViewLabel):

    path = ''

    def __init__(self, path='', **kwargs):
        super(FolderLabel, self).__init__(**kwargs)

        self.path = path

'''
    This is a custom Tree View to view the folders
'''
class FolderTreeView(TreeView):

    def __init__(self, notes_view,  **kwargs):
        super(FolderTreeView, self).__init__(**kwargs)

        self.hide_root=True
        self.bind(minimum_height = self.setter('height'))

        self.notes_view = notes_view

        # Traverse the db directory
        hobbes_folder = os.path.dirname(os.path.abspath(__file__))
        hobbes_db     = os.path.join(hobbes_folder, 'db')

        added = []

        # Helper functions used to sort
        convert = lambda text: int(text) if text.isdigit() else text 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 

        for root, dirs, files in os.walk(hobbes_db):

            # Alfabetical order
            dirs.sort(key=alphanum_key)

            level = root.replace(hobbes_db, '').count(os.sep)

            # Ignore the db folder and the attachments folder
            if root == hobbes_db or os.path.basename(root) == '.attachments_db':

                continue

            # Add the rest of folders recursively
            if level == 1:

                added = []
                added.append(self.add_node(FolderLabel(text=os.path.basename(root), path=root)))
            else:

                added.append(self.add_node(FolderLabel(text=os.path.basename(root), path=root), added[level-2]))

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


        self.add_widget(audio_layout)
        self.add_widget(self.notes_view_scroll)
        self.add_widget(self.note_text_input)

    # This method will be in charge of all the input actions
    def on_touch_down(self, touch):

        # Handle TreeView touch
        if self.folder_tree_view_scroll.collide_point(touch.x, touch.y):

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

class HobbesApp(App):

    def build(self):
        return MainScreen()

if __name__ == '__main__':
    HobbesApp().run()