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

            added = {}
            added[level] = tree.add_node(FolderLabel(text=os.path.basename(root), path=root))

            path_dictionary[root] = added[level]

        else:
            added[level] = tree.add_node(FolderLabel(text=os.path.basename(root), path=root), added[level-1])
            path_dictionary[root] = added[level]


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
        self.hobbes_db = hobbes_db
        self.active_node = None

        populate_tree(self, self.hobbes_db, self.path_dictionary)

        # Context menu
        self.context_menu = FolderTreeViewContextMenu(size_hint=(.3, .5), notes_view=self.notes_view, tree_view=self)

    # Refresh the tree view
    def rebuild_tree_view(self):

        self.path_dictionary = {}

        aux_path = os.path.join(self.active_node.path, self.active_node.text)

        # Delete all children
        for node in [i for i in self.iterate_all_nodes()]:

            self.remove_node(node)

        # Add the new children
        populate_tree(self, self.hobbes_db, self.path_dictionary)

        print("Hi", os.path.dirname(aux_path), os.path.dirname(aux_path))

        self.active_node = self.path_dictionary[os.path.dirname(aux_path)]


        if self.active_node != None:

            # Try to reopen the current folder if it exists
            # Find the tree path until this node
            traversed_tree = []
            traversed_tree.append(self.active_node)
            parent_node = self.active_node.parent_node

            while parent_node != self.root:

                traversed_tree.insert(0, parent_node)
                parent_node = parent_node.parent_node

            # Open the nodes until the selected node
            for t in traversed_tree:

                if not t.is_open:

                    self.toggle_node(t)

            # And select the node
            self.select_node(self.active_node)

    def custom_event_handler(self, touch):

        if touch.button != 'scrolldown' and touch.button != 'scrollup':

            self.active_node = self.get_node_at_pos((touch.x, touch.y))
            
            if self.active_node != None:

                self.notes_view.add_notes(self.active_node.path)

                if touch.button == 'right' or touch.is_double_tap:

                    self.context_menu.menu_opened(self.active_node)

                    return True

            # There is no node under the cursor
            else:

                print("Not a leaf")

    def folder_opened_without_touch(self, node):

        self.active_node = node
        
        if self.active_node != None:

            self.notes_view.add_notes(self.active_node.path)