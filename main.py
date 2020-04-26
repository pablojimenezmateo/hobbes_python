import kivy
kivy.require('1.11.1') # Kivy version

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

'''
    This is a custom Tree View to view the folders
'''
class FolderTreeView(TreeView):

    def __init__(self, **kwargs):
        super(FolderTreeView, self).__init__(**kwargs)

        self.hide_root=True
        self.bind(minimum_height = self.setter('height'))

        # Tree test
        n1 = self.add_node(TreeViewLabel(text='Folder 1'))

        for i in range(50):

            self.add_node(TreeViewLabel(text='Subfolder ' + str(i+1)), n1)
 
        n2 = self.add_node(TreeViewLabel(text='Folder 2'))
        self.add_node(TreeViewLabel(text='SubItem 5'), n2) 

        # Context menu
        self.context_menu = FolderTreeViewContextMenu(size_hint=(.2, .2))

    def custom_event_handler(self, touch):

        print("On tree")

        active_node = self.get_node_at_pos((touch.x, touch.y))
        
        if active_node != None:

            print("Node:", active_node.text)

            if touch.button == 'right':

                self.context_menu.menu_opened(active_node)
                return True
'''
    Each of the notes is represented by one button
'''
class NoteButton(Button):

    def __init__(self, context_menu, **kwargs):
        super(NoteButton, self).__init__(**kwargs)

        self.context_menu = context_menu

        # Text color
        self.color = (0, 0, 0, 1)

        # Button color
        self.background_color  = (0.569, 0.667, 0.616, 1)
        
    def on_touch_down(self, touch):

        if self.collide_point(touch.x, touch.y):

            print("I have been touched ", self.text)

            if touch.button == 'right':

                self.context_menu.menu_opened(self)

            return super(NoteButton, self).on_touch_down(touch)

'''
    This is the column that shows notes
'''
class NoteView(GridLayout):

    def __init__(self, **kwargs):
        super(NoteView, self).__init__(**kwargs)

        self.bind(minimum_height = self.setter('height'))

        # Context menu
        self.context_menu = NoteViewContextMenu(size_hint=(.2, .2))

        # Notes test
        for i in range(50):
            self.add_widget(NoteButton(context_menu=self.context_menu, text='Note ' + str(i+1), size_hint=(1, None), size=(0, 20), text_size=(self.width, None), halign='left'))

'''
    This will be used to edit notes
'''
class NoteTextInput(TextInput):

    def __init__(self, **kwargs):
        super(NoteTextInput, self).__init__(**kwargs)

        self.font_size = 20

class NoteTextRenderer(Label):

    def __init__(self, **kwargs):
        super(NoteTextRenderer, self).__init__(**kwargs)

        self.markup = True
        self.font_size = 20
        self.halign ='right'
        self.valign = 'middle'
'''
    Combination of the text editor and renderer
'''
class NoteTextPanel(BoxLayout):

        note_text_input = NoteTextInput(size_hint=(.5, 1), multiline=True)
        note_text_renderer = NoteTextRenderer(size_hint=(.5, 1))

        def __init__(self, **kwargs):
            super(NoteTextPanel, self).__init__(**kwargs)

            self.orientation = 'horizontal'
            self.add_widget(self.note_text_input)
            self.note_text_input.bind(text=self.on_input_text)

            self.add_widget(self.note_text_renderer)

        def on_input_text(self, instance, text):

            self.note_text_renderer.text = text

'''
    This is the Layout of the main screen of the application
'''
class MainScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Orientation of the Box Layouts
        self.orientation='horizontal'

        # Folders view
        self.folder_tree_view_scroll = ScrollView(size_hint=(.2, 1))
        self.folder_tree_view = FolderTreeView(size_hint_y=None)
        self.folder_tree_view_scroll.add_widget(self.folder_tree_view)

        # Notes view
        self.notes_view_scroll = ScrollView(size_hint=(.2, None))
        self.notes_view = NoteView(cols=1, size_hint=(1, None))
        self.notes_view_scroll.add_widget(self.notes_view)

        # Notes input
        self.note_text_input = NoteTextPanel(size_hint=(.6, 1))

        self.add_widget(self.folder_tree_view_scroll)
        self.add_widget(self.notes_view_scroll)
        self.add_widget(self.note_text_input)

    # This method will be in charge of all the input actions
    def on_touch_down(self, touch):

        # Handle TreeView touch
        if touch.button != 'scrolldown' and touch.button != 'scrollup' and self.folder_tree_view_scroll.collide_point(touch.x, touch.y):

            # Save the touch since we are making coordinates transform
            touch.push()

            # We need to fix the coordinate system since the scroll has moved the widget
            touch.apply_transform_2d(self.folder_tree_view_scroll.to_local)
            self.folder_tree_view.custom_event_handler(touch)

            # Restore touch
            touch.pop()

        return super(MainScreen, self).on_touch_down(touch)

class HobbesApp(App):

    def build(self):
        return MainScreen()

if __name__ == '__main__':
    HobbesApp().run()