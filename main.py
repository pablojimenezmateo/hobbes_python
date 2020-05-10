import kivy
kivy.require('1.11.1') # Kivy version

from kivy.config import Config
# By default kivy exits when Esc is pressed, overwrite it
Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'maxfps', '30')
Config.set('kivy','window_icon','media/images/icon.png')

from kivy.app import App
from src.gui.context_menu.context_button import *
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.clock import Clock

# Local imports
from src.util.git_functions import *
from src.util.text_indexing_functions import *

# Popup
from src.gui.popup.search_popup import *

# Views
from src.gui.view.folder_view import *
from src.gui.view.note_view import *

# Text panel
from src.gui.note_panel.note_panel import *

# Music
from src.gui.music_slider.music_slider import *

# Filesystem
import os

# Global definitions
# This is the path where notes will be stored and read from
hobbes_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')

'''
    TODO:

        - Change pygame for other audio engine
        - Graphically allow to move a note/folder
            - This can be achieved by putting a flag in MainScreen, so that the touch on the tree have a different
                meaning when actived, and are handled by another handler

        - Fix popup layouts -> Change to modal views
        - Add option to export to pdf
        - Implement contextual menu options
        - Allow to create root folders if no folder exists
'''
      
'''
    This is the Layout of the main screen of the application
'''
class MainScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Orientation of the Box Layouts
        self.orientation='horizontal'

        # Notes input panel
        self.note_text_input = NoteTextPanel(size_hint=(.6, 1), hobbes_db=hobbes_db)

        # Notes view
        self.notes_view_scroll = ScrollView(size_hint=(.2, None))
        self.notes_view = NoteView(note_text_panel=self.note_text_input, cols=1, size_hint=(1, None), hobbes_db=hobbes_db)
        self.notes_view_scroll.add_widget(self.notes_view, 0)

        # Folders view
        self.folder_tree_view_scroll = ScrollView(size_hint=(1, 1))
        self.folder_tree_view = FolderTreeView(size_hint_y=None, notes_view=self.notes_view, hobbes_db=hobbes_db)
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

        # Save current note when exiting
        Window.bind(on_close=self.on_close)

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

    # Save the current note on exit
    def on_close(self, args):

        self.note_text_input.save_note()

# Main app
class HobbesApp(App):

    def build(self):

        # Create the db folder if it does not exist
        if not os.path.exists(hobbes_db):

            os.mkdir(hobbes_db)

        return MainScreen()

if __name__ == '__main__':

    HobbesApp().run()