import kivy
kivy.require('1.11.1') # Kivy version

from kivy.config import Config
# By default kivy exits when Esc is pressed, overwrite it
Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'maxfps', '30')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.rst import RstDocument
from kivy.clock import Clock
from kivy.uix.slider import Slider
from kivy.uix.dropdown import DropDown
from kivy.uix.modalview import ModalView
from kivy.uix.image import Image

# Local imports
from src.util.git_functions import *
from src.util.text_indexing_functions import *

# Popup
from src.gui.popup.search_popup import *

# Context menus
from src.gui.context_menu.folder_context_menu import *
from src.gui.context_menu.note_context_menu import *

# Filesystem
import os
import subprocess
import platform

# Used for natural sorting
import re 

# For audio playing
from pygame import mixer

# For the attachments
import hashlib
from shutil import copyfile

# To export to PDF
from markdown import markdown

# To open URLs when clicked 
import webbrowser

# Global definitions
# This is the path where notes will be stored and read from
hobbes_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')


NOTE_VIEW_NOT_ACTIVE_NOTE_COLOR = (1, 1, 1, 1)
NOTE_VIEW_ACTIVE_NOTE_COLOR = (1, 1, 1, 0.5)

NOTE_INPUT_FONT_SIZE = 24

NOTE_RENDERER_BACKGROUND_COLOR = (1, 1, 1, 1)
NOTE_RENDERER_UNDERLINE_COLOR = '000000FF'
NOTE_RENDERER_FONT_SIZE = 48


'''
    TODO:

        - Add option to export to pdf
        - Implement contextual menu options

        - Renderer
            - Finish attachments that are not images

        - When the app closes, save current note
'''


""" Sort the given iterable in the way that humans expect.""" 
def sorted_nicely(l): 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key=alphanum_key)


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
def populate_tree(tree, path, path_dictionary):

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

            path_dictionary[root] = added[-1]
        else:

            added.append(tree.add_node(FolderLabel(text=os.path.basename(root), path=root), added[level-2]))

            path_dictionary[root] = added[-1]

'''
    This is a custom Tree View to view the folders
'''
class FolderTreeView(TreeView):

    # This is a quick way to find the tree node given the path
    path_dictionary = {}

    def __init__(self, notes_view,  **kwargs):
        super(FolderTreeView, self).__init__(**kwargs)

        self.hide_root=True
        self.bind(minimum_height = self.setter('height'))

        self.notes_view = notes_view

        populate_tree(self, hobbes_db, self.path_dictionary)

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

    def folder_opened_without_touch(self, node):

        active_node = node
        
        if active_node != None:

            self.notes_view.add_notes(active_node.path)

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
        self.context_menu = NoteViewContextMenu(size_hint=(.2, .2))

    def add_notes(self, path):

        self.clear_widgets()
        self.path_dictionary = {}

        for file in sorted_nicely(os.listdir(path)):
            if file.endswith(".txt"):

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

'''
    This will be used to edit notes
'''
class NoteTextInput(TextInput):

    def __init__(self, **kwargs):
        super(NoteTextInput, self).__init__(**kwargs)

        self.font_size = NOTE_INPUT_FONT_SIZE
        self.background_normal = ''
        self.padding = [16, 15, 6, 6]

class NoteTextRenderer(ScrollView): 

    def __init__(self, **kwargs):
        super(NoteTextRenderer, self).__init__(**kwargs)

        self.label = self.ids.label

        # Format options
        self.label.padding = (16, 15)
        self.label.font_size = NOTE_INPUT_FONT_SIZE

        #Listen for hiperlinks
        self.label.bind(on_ref_press=self.reference_click)

        # Stored images
        self.images = {}

        # This dirty hack is to avoid a bug
        # that would cause the bind [self.bind(width=self.resize_width)] to be called on loop
        # Just check if the Window has been resized
        self.prev_width = self.width

        self.images_need_rerender = False
        self.is_new_note = False

        # We need to keep an eye to re render the images
        Clock.schedule_interval(self.render_images, 0.1)

        self.original_text = ''

        self.current_note_path = ''

    def on_new_note_open(self, current_note_path, text):

        self.current_note_path = current_note_path

        for path, w in self.images.items():

            self.label.remove_widget(w)

        self.images = {}

        self.is_new_note = True

        self.set_text(current_note_path, text)


    def set_text(self, current_note_path, text):

        self.original_text = text

        self.images_need_rerender = True

        self.current_note_path = current_note_path

        # First parse the text for links
        link_re = re.compile(r'^!?\[(local[^\]]+)\]\(([^)]+)\)$', flags=re.MULTILINE)

        # Load all the images
        for ind, match in enumerate(link_re.findall(text)):

            # Convert attachment links correctly
            # We need to get the relative path, translate it to an absolute path
            # and then add it to an [anchor] tag

            # Get the absolute path of the attachment from the relative path
            saved_path = os.getcwd()
            os.chdir(os.path.split(current_note_path)[0]) 
            abs_attachment_path = os.path.abspath(match[1])
            os.chdir(saved_path)

            if match[0] == 'local_image':

                if abs_attachment_path not in self.images:

                    wimg = Image(source=abs_attachment_path)
                    self.label.add_widget(wimg)
                    self.images[abs_attachment_path] = wimg

                    print("Loading", abs_attachment_path)

                self.original_text = self.original_text.replace('![local_image](' + match[1] + ')', '[anchor=' + abs_attachment_path + '].')

        # Get the absolute path with os.path.abspath(rel_path)
        if self.is_new_note:

            self.label.text = self.original_text
            self.is_new_note = False

    # This function handles when a [ref] is clicked
    def reference_click(self, instance, value):

        # Check if text is valid URL (https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not)
        url_regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(url_regex, value) is not None:

            webbrowser.open(value)
            return

        # It is a file
        if 'code_block_hobbes' not in value:

            # Get the absolute path of the attachment from the relative path
            saved_path = os.getcwd()
            os.chdir(os.path.split(self.current_note_path)[0]) 
            abs_attachment_path = os.path.abspath(value)
            os.chdir(saved_path)
            
            if platform.system() == 'Darwin':       # macOS

                subprocess.call(('open', abs_attachment_path))
            elif platform.system() == 'Windows':    # Windows

                os.startfile(abs_attachment_path)
            else:                                   # linux variants
                subprocess.call(('xdg-open', abs_attachment_path))

    def render_images(self, dt):

        # If the width has changed
        if self.prev_width != self.width:
            self.images_need_rerender = True

            self.prev_width = self.width

        if self.images_need_rerender:

            self.images_need_rerender = False

            # First modify the text
            aux_text = self.original_text

            for name, anc in self.label.anchors.items():

                i = self.images[name]

                i.width = self.width - 32
                i.height = self.width/i.image_ratio

                # After adding the image, I need to add enough whitespaces on that position so that the image does not cover the text
                vspace = round(i.height / (NOTE_INPUT_FONT_SIZE + 4)) # That 4 is for intelining spacing

                aux_text = aux_text.replace('[anchor=' + name + '].', '\n'*vspace + '[anchor=' + name + ']')


            # Partial translation to kivy Markdown
            # Code blocks
            aux_text = re.sub(r'\`{3}(\s*[a-z]*\s*)([^\`]+)\`{3}', "[ref=code_block_hobbes][font=media/fonts/FiraCode-Regular.ttf]\\2[/font][/ref]", aux_text)

            # Links
            aux_text = re.sub(r"\[(.*?)\]\((.*?)\)", "[u][color=#0000EE][ref=\\2]\\1[/ref][/color][/u]", aux_text)

            # Bold
            aux_text = re.sub(r"\B([*_]{2})\b(.+?)\1\B", "[b]\\2[/b]", aux_text)

            # Italic
            aux_text = re.sub(r"\B([*_])\b(.+?)\1\B", "[i]\\2[/i]", aux_text)

            # Titles
            aux_text = re.sub(r"(?m)^#####\s+(.*?)\s*#*$", "[size=40][b]\\1[/b][/size]", aux_text)
            aux_text = re.sub(r"(?m)^####\s+(.*?)\s*#*$",  "[size=50][b]\\1[/b][/size]", aux_text)
            aux_text = re.sub(r"(?m)^###\s+(.*?)\s*#*$",   "[size=60][b]\\1[/b][/size]", aux_text)
            aux_text = re.sub(r"(?m)^##\s+(.*?)\s*#*$",    "[size=70][b]\\1[/b][/size]", aux_text)
            aux_text = re.sub(r"(?m)^#\s+(.*?)\s*#*$",     "[size=80][b]\\1[/b][/size]", aux_text)

            self.label.text = aux_text

            # We need to do this one tick after the label has rendered
            Clock.schedule_once(self.draw_backgrounds)
            Clock.schedule_once(self.move_images)

    def move_images(self, dt):

        # Then position the images
        for name, anc in self.label.anchors.items():

            i = self.images[name]
            i.pos = (16, self.label.texture_size[1] - self.label.anchors[name][1])

    # This functions are used to add a background to the special blocks
    @staticmethod
    def get_x(label, ref_x):
        """ Return the x value of the ref/anchor relative to the canvas """
        return label.center_x - label.texture_size[0] * 0.5 + ref_x

    @staticmethod
    def get_y(label, ref_y):
        """ Return the y value of the ref/anchor relative to the canvas """
        # Note the inversion of direction, as y values start at the top of
        # the texture and increase downwards
        return label.center_y + label.texture_size[1] * 0.5 - ref_y

    def draw_backgrounds(self, dt):

        label = self.label
        label.canvas.remove_group('code_background')

        # Draw a green surround around the refs. Note the sizes y inversion
        for name, boxes in label.refs.items():

            if 'code_block_hobbes' in name:
                for box in boxes:
                    with label.canvas:
                        Color(0, 0, 0, 0.15)
                        Rectangle(pos=(self.get_x(label, box[0]),
                                       self.get_y(label, box[1])),
                                  size=(self.width - 32,
                                        box[1] - box[3]), group='code_background')

           
'''
    Combination of the text editor and renderer, I  write my notes in Markdown but the renderer is in reStructuredText
'''
class NoteTextPanel(BoxLayout):

        # The path of the active note
        current_note = None

        # This variable will be used to keep track if the note has new content
        # that needs to be saved, instead of mindlessly saving it every 30
        # seconds
        current_note_saved = True

        # Possible view status: 0 = split, 1 = Note, 2 = renderer
        toggle_status = 0

        def __init__(self, **kwargs):
            super(NoteTextPanel, self).__init__(**kwargs)

            self.orientation = 'horizontal'

            self.note_text_input    = NoteTextInput(size_hint=(.5, 1), multiline=True)
            self.note_text_renderer = NoteTextRenderer(size_hint=(.5, None))

            self.add_widget(self.note_text_input)

            # Listen to input text and render it realtime
            self.note_text_input.bind(text=self.on_input_text)

            self.add_widget(self.note_text_renderer)#self.note_text_rendere_scroll)

            # Autosave each 30 seconds
            Clock.schedule_interval(self.autosave, 30)

            # Listen for a dropped file
            Window.bind(on_dropfile=self.on_file_drop)

        def on_input_text(self, instance, text):

            # Since there is new text, we need to save this note
            self.current_note_saved = False

            self.note_text_renderer.set_text(self.current_note, text)

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
            self.note_text_renderer.on_new_note_open(self.current_note, text)

            # Make sure the scroll is on top
            self.note_text_input.cursor = (0, 0)

        # Saves the contents of the current editor to the current note
        def save_note(self):

            if self.current_note != None and not self.current_note_saved:

                print("Writting", self.note_text_input.text, " to", self.current_note)

                with open(self.current_note, 'w') as note:
                    note.write(self.note_text_input.text)

                self.current_note_saved = True

                # Reindex the note
                reindex_one_note(hobbes_db, '.text_index', self.current_note)

        # Autosave function
        def autosave(self, dt):

            self.save_note()

        # Handle dropped files
        def on_file_drop(self, window, file_path):

            if self.current_note != None:

                print(file_path)

                # The file will be renamed to its hash to try to avoid name collitions
                file_hash = hashlib.sha256()

                with open(file_path, 'rb') as f:

                    fb = f.read(65536)

                    while len(fb) > 0:

                        file_hash.update(fb) 
                        fb = f.read(65536)

                # Create the file on the .attachments folder
                dst_path = self.current_note.replace(hobbes_db, '').split(os.sep)[1]
                base_folder = dst_path
                dst_path = os.path.join(hobbes_db, dst_path)
                dst_path = os.path.join(dst_path, '.attachments')

                # Create the attachment folder if it does not exist
                if not os.path.exists(dst_path):

                    os.mkdir(dst_path)

                extension = os.path.basename(file_path.decode("utf-8", "strict")).split(".")[1]
                old_name = os.path.basename(file_path.decode("utf-8", "strict"))
                new_name = file_hash.hexdigest() + '.' + extension

                is_image = False

                if extension in ['png', 'jpg', 'jpeg', 'gif']:

                    is_image = True

                try:
                    copyfile(file_path, os.path.join(dst_path, new_name))

                except:

                    print("Error copying file")

                # Add the correctly formated relative URL
                attachment_path = os.path.join(hobbes_db, os.path.join(base_folder, '.attachments'))
                relative_path = os.path.relpath(os.path.join(hobbes_db, attachment_path), os.path.split(self.current_note)[0])

                if is_image:

                    self.note_text_input.insert_text('![local_image](' + os.path.join(relative_path, new_name) + ')')
                else:

                    self.note_text_input.insert_text('[file: ' + old_name + '](' + os.path.join(relative_path, new_name) + ')')


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
        self.search_popup = SearchPopup(size_hint=(None, None), size=(400, 0), folder_tree_view=self.folder_tree_view, notes_view=self.notes_view, hobbes_db=hobbes_db)

        '''
            Indexing new files
        '''
        index_my_docs(hobbes_db, '.text_index', False)

        '''
            Git sync
        '''
        # Create a commit every 30 seconds and a push every 5 minutes
        Clock.schedule_interval(self.do_commit, 30)
        Clock.schedule_interval(self.do_push, 300)


    # This method commits all top level folders from the db
    def do_commit(self, dt):

        for path in self.folder_tree_view.path_dictionary:

            relative_path = path.replace(hobbes_db, '')

            level = relative_path.count(os.sep)

            if level == 1:

                print("Commit ", path)
                git_commit_threaded(path)

    # This method pushes all top level folders from the db
    def do_push(self, dt):

        for path in self.folder_tree_view.path_dictionary:

            relative_path = path.replace(hobbes_db, '')

            level = relative_path.count(os.sep)

            if level == 1:

                print("Push ", path)
                git_commit_and_push_threaded(path)

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

            # This opens and closes the search
            if self.search_popup.active:

                self.search_popup.dismiss()
            else:

                self.search_popup.clear_all()
                self.search_popup.open()


class HobbesApp(App):

    def build(self):

        # Create the db folder if it does not exist
        if not os.path.exists(hobbes_db):

            os.mkdir(hobbes_db)

        return MainScreen()

if __name__ == '__main__':
    HobbesApp().run()