from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from src.util.text_indexing_functions import do_search
import os

# Colors
SEARCH_POPUP_BACKGROUND_COLOR = (0, 0, 0, 0)
SEARCH_BUTTON_TEXT_COLOR = (0, 0, 0, 1)


'''
    SearchButton
'''
class SearchButton(Button):

    def __init__(self, path, **kwargs):
        super(SearchButton, self).__init__(**kwargs)

        self.path = path


'''
    Search popup
'''
class SearchPopup(ModalView):

    def __init__(self, folder_tree_view, notes_view, hobbes_db, **kwargs):

        super(SearchPopup, self).__init__(**kwargs)

        self.folder_tree_view = folder_tree_view
        self.notes_view = notes_view
        self.hobbes_db = hobbes_db

        # Remove background
        self.background = 'media/images/transparent.png'
        self.background_color = SEARCH_POPUP_BACKGROUND_COLOR

        # To check if it is active
        self.active = False
        self.bind(on_open=self.toggle_active)
        self.bind(on_dismiss=self.toggle_active)

        # Put it at the top
        self.pos_hint = {'top': 0.9}

        # The buttons will be added to a BoxLayout
        self.layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.textinput = TextInput(text='', multiline=False, size_hint=(1, None), size=(0, 30))
        self.layout.add_widget(self.textinput)

        self.add_widget(self.layout)

        # Search when enter is pressed
        self.textinput.bind(on_text_validate=self.do_search)

        self.buttons = []

    def toggle_active(self, args):

        self.active = not self.active

    def clear_all(self):

        self.dismiss()
        self.textinput.text=''
        self.clear_results()

    def clear_results(self):

        for btn in self.buttons:

            self.layout.remove_widget(btn)

        self.buttons = []

    def do_search(self, textinput):

        self.clear_results()

        # Search
        results = do_search(textinput.text, self.hobbes_db)

        for hit in results:

            beautiful_path = hit['path'].replace(self.hobbes_db, '')
            beautiful_path = '>'.join(beautiful_path.split(os.sep)[1:-1]) + '>' + hit['title']

            print(beautiful_path)

            btn = SearchButton(text=beautiful_path, path=hit['path'], color=SEARCH_BUTTON_TEXT_COLOR)
            self.layout.add_widget(btn)

            self.buttons.append(btn)

        # We move the layout downward, since appending buttons makes it move upward
        self.layout.pos = (self.layout.x, self.layout.y - 30 * len(results))

    def on_touch_down(self, touch):

        for btn in self.buttons:

            if btn.collide_point(touch.x, touch.y) and touch.button == 'left':

                tree_node = self.folder_tree_view.path_dictionary[os.path.dirname(btn.path)]

                # Find the tree path until this node
                traversed_tree = []
                traversed_tree.append(tree_node)
                parent_node = tree_node.parent_node

                while parent_node != self.folder_tree_view.root:

                    traversed_tree.insert(0, parent_node)
                    parent_node = parent_node.parent_node

                # Open the nodes until the selected node
                for t in traversed_tree:

                    if not t.is_open:

                        self.folder_tree_view.toggle_node(t)

                # And select the node
                self.folder_tree_view.select_node(tree_node)

                # Load the notes
                self.folder_tree_view.folder_opened_without_touch(tree_node)

                # Open the note
                self.notes_view.activate_note(self.notes_view.path_dictionary[btn.path])
                break

        return super(SearchPopup, self).on_touch_down(touch)


    # Set the focus when opened
    def on_open(self):

        self.textinput.focus = True