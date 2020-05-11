from src.gui.popup.info_popup import *
from src.gui.popup.textinput_popup import *
from src.gui.popup.confirmation_popup import *
from src.gui.context_menu.context_button import *
from src.util.attachments_consistency_functions import *

from kivy.uix.modalview import ModalView

from src.util.text_indexing_functions import *

import os
from functools import partial
from shutil import move


'''
    Contextual menu for the folder view
'''
class FolderTreeViewContextMenu(ModalView):

    def __init__(self, notes_view, tree_view, **kwargs):
        super(FolderTreeViewContextMenu, self).__init__(**kwargs)

        self.title = "Menu"
        self.notes_view = notes_view
        self.tree_view = tree_view

        self.context_menu = BoxLayout(orientation='vertical')

        # Create the options
        new_note_button        = ContextButton(text="New note")
        new_folder_button      = ContextButton(text="New folder")
        rename_folder_button   = ContextButton(text="Rename folder")
        new_root_folder_button = ContextButton(text="New root folder")

        # Special dialogues are needed for the following options
        move_folder_button     = ContextButton(text="Move folder")
        export_folder_button   = ContextButton(text="Export folder to PDF")
        delete_folder_button   = ContextButton(text="Delete folder")

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

        self.add_widget(self.context_menu)

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


        self.tree_view.set_moving_folder_mode(self.move_folder)
        
        self.dismiss()

        # If the user doubleclicks on another folder, the folder moves there

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

        if not os.path.isfile(os.path.join(self.current_folder.path, text + '.md')):

            with open(os.path.join(self.current_folder.path, text) + '.md', 'w'):

                pass

            # Refresh so the newly created note appears
            self.notes_view.add_notes(self.current_folder.path)
        else:

            info = InfoPopup(title="Create note", message="ERROR: File already exists", size_hint=(.3, .2))
            info.open()

        popup.dismiss()

    def create_folder(self, popup, text):

        if not os.path.isdir(os.path.join(self.current_folder.path, text)):

            os.mkdir(os.path.join(self.current_folder.path, text))

            # Refresh so the newly created note appears
            self.tree_view.rebuild_tree_view()
        else:

            info = InfoPopup(title="Create folder", message="ERROR: Folder already exists", size_hint=(.3, .2))
            info.open()

        popup.dismiss()

    def create_root_folder(self, popup, text):

        if not os.path.isdir(os.path.join(self.tree_view.hobbes_db, text)):

            os.mkdir(os.path.join(self.tree_view.hobbes_db, text))

            # Refresh so the newly created note appears
            self.tree_view.rebuild_tree_view()
        else:

            info = InfoPopup(title="Create root folder", message="ERROR: Folder already exists", size_hint=(.3, .2))
            info.open()

        popup.dismiss()

    def rename_folder(self, popup, new_name):

        popup.dismiss()

        upper_folder = os.path.split(self.current_folder.path)[0]

        new_path = os.path.join(upper_folder, new_name)

        if not os.path.isdir(new_path):

            # Reindex all the notes inside that folder
            reindex_one_moving_folder(self.tree_view.hobbes_db, '.text_index', self.current_folder.path, new_path)

            # Move the file
            move(self.current_folder.path, new_path)

            # Refresh tree
            self.tree_view.rebuild_tree_view()

        else:

            info = InfoPopup(title="Renaming note", message="ERROR: Note already exists", size_hint=(.3, .2))
            info.open()


    def move_folder(self, new_path):

        # Here I need to check all the notes and fix their relative paths to the attachments
        if self.current_folder != None:

            # Allow to pick where the folder goes
            # Check that the path is valid
            # Check that there is not a folder with that name already

            #fix_folder_consistency(self.current_folder.path, '/home/gef/Documents/Hobbes-many/hobbes_debug/hobbes_python/db/Work/IMDEA/', self.tree_view.hobbes_db)
            print("Moving folder", self.current_folder.path, " to", new_path)
            self.tree_view.rebuild_tree_view()


    def export_folder(self, popup):

        if self.current_folder != None:

            print("Exporting folder", self.current_folder.text)
            popup.dismiss()

    def delete_folder(self, popup):

        # IMPORTANT: Set self.tree_view.active_node = None

        if self.current_folder != None:

            print("Deleting folder", self.current_folder.text)
            popup.dismiss()