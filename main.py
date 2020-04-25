import kivy
kivy.require('1.11.1') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
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

        # Tree test
        #self.size_hint=(.2, 5)
        self.hide_root=True
        #self.tree_view.size_hint=(1, 1)
        self.bind(minimum_height = self.setter('height'))

        n1 = self.add_node(TreeViewLabel(text='Folder 1'))

        for i in range(50):

            self.add_node(TreeViewLabel(text='Subfolder ' + str(i+1)), n1)
 

        n2 = self.add_node(TreeViewLabel(text='Folder 2'))
        self.add_node(TreeViewLabel(text='SubItem 5'), n2) 


        # Context menu
        self.context_menu = FolderTreeViewContextMenu(size_hint=(.2, .2))

    def custom_event_handler(self, touch):

        print("On tree")

        active_node = self.get_node_at_pos(touch.pos)
        
        if active_node != None:

            print("Node:", self.get_node_at_pos(touch.pos).text)

            if touch.button == 'right':

                self.context_menu.menu_opened(active_node)
                return True

        return super(FolderTreeView, self).on_touch_down(touch)


class NoteLabel(Label):

    def __init__(self, context_menu, **kwargs):
        super(NoteLabel, self).__init__(**kwargs)

        self.context_menu = context_menu
        self.color = (1, 0, 0, 1)

        Rectangle(pos=self.pos, size=self.size)
        
    def on_touch_down(self, touch):

        if self.collide_point(touch.x, touch.y):

            print("I have been touched ", self.text)


            if touch.button == 'right':

                self.context_menu.menu_opened(self)

            return True


class NoteButton(Button):

    def __init__(self, context_menu, **kwargs):
        super(NoteButton, self).__init__(**kwargs)

        self.context_menu = context_menu

        # Text color
        self.color = (0, 0, 0, 1)

        # Button color
        #self.background_normal = ''
        #self.background_down   = ''
        self.background_color  = (0.569, 0.667, 0.616, 1)
        
    def on_touch_down(self, touch):

        if self.collide_point(touch.x, touch.y):

            print("I have been touched ", self.text)

            if touch.button == 'right':

                self.context_menu.menu_opened(self)

            return super(NoteButton, self).on_touch_down(touch)

class NoteView(GridLayout):

    def __init__(self, **kwargs):
        super(NoteView, self).__init__(**kwargs)

        self.bind(minimum_height = self.setter('height'))

        # Create the StackLayout
        #self.layout = StackLayout(orientation='tb-lr', size_hint_y=5)

        # Context menu
        self.context_menu = NoteViewContextMenu(size_hint=(.2, .2))

        # Notes test
        #self.size_hint=(.2, None)
        #self.add_widget(Label(text="Test", size_hint=(1, None), size=(0, 20)))

        for i in range(50):
            self.add_widget(NoteButton(context_menu=self.context_menu, text='Note ' + str(i+1), size_hint=(1, None), size=(0, 20), text_size=(self.width, None), halign='left'))

#    def custom_event_handler(self, touch):

#        return super(NoteView, self).on_touch_down(touch)

class NoteTextInput(TextInput):

    def __init__(self, **kwargs):
        super(NoteTextInput, self).__init__(**kwargs)

'''
    This is the Layout of the main screen of the application
'''
class MainScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Orientation of the Box Layouts
        self.orientation='horizontal'

        # Folders view
        self.folder_tree_view = ScrollView(size_hint=(.2, 1))
        self.folder_tree_view.add_widget(FolderTreeView(size_hint_y=None))

        # Notes view
        self.notes_view = ScrollView(size_hint=(.2, None))
        self.notes_view.add_widget(NoteView(cols=1, size_hint=(1, None)))

        # Notes input
        self.note_text_input = NoteTextInput(size_hint=(.6, 1), font_size=20)

        self.add_widget(self.folder_tree_view)
        self.add_widget(self.notes_view)
        self.add_widget(self.note_text_input)

    # This method will be in charge of all the input actions
    def on_touch_down(self, touch):

        print("Fired after the event has been dispatched! ", touch.x, touch.y)
        print("Touch button: ", touch.button)

        if self.folder_tree_view.collide_point(touch.x, touch.y):

            return super(MainScreen, self).on_touch_down(touch)

            #return self.folder_tree_view.custom_event_handler(touch)

        #elif self.notes_view.collide_point(touch.x, touch.y):
        #
        #   return self.notes_view.custom_event_handler(touch)

        else:

            print("Outside tree")
            return super(MainScreen, self).on_touch_down(touch)

class HobbesApp(App):

    def build(self):
        return MainScreen()


if __name__ == '__main__':
    HobbesApp().run()