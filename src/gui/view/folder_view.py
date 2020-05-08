from kivy.uix.treeview import TreeView, TreeViewLabel
import re
import os

from src.gui.context_menu.folder_context_menu import *

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

    def __init__(self, notes_view, hobbes_db, **kwargs):
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