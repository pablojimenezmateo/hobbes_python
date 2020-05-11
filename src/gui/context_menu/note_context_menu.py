from src.gui.popup.info_popup import *
from src.gui.popup.textinput_popup import *
from src.gui.popup.confirmation_popup import *
from src.gui.context_menu.context_button import *
from src.util.attachments_consistency_functions import *

from src.util.text_indexing_functions import *

from kivy.uix.modalview import ModalView

from markdown import markdown
from shutil import move

'''
    Contextual menu for the note view
'''
class NoteViewContextMenu(ModalView):

    def __init__(self, hobbes_db, note_view, **kwargs):
        super(NoteViewContextMenu, self).__init__(**kwargs)

        self.hobbes_db = hobbes_db
        self.note_view = note_view
        self.title = "Menu"
        self.tree_view = None

        self.context_menu = BoxLayout(orientation='vertical')

        # Create the options
        rename_note_button   = ContextButton(text="Rename note")
        move_note_button     = ContextButton(text="Move note")
        delete_note_button   = ContextButton(text="Delete note")
        export_note_button   = ContextButton(text="Export note to PDF")
        self.context_menu.add_widget(rename_note_button)
        self.context_menu.add_widget(move_note_button)
        self.context_menu.add_widget(delete_note_button)
        self.context_menu.add_widget(export_note_button)

        # Bind the buttons to functions
        rename_note_button.bind(on_release = self.rename_note_popup) 
        move_note_button.bind(on_release = self.move_note_popup)
        delete_note_button.bind(on_release = self.delete_note_popup)
        export_note_button.bind(on_release = self.export_note_popup)

        self.add_widget(self.context_menu)

        self.current_note = None

    def set_tree_view(self, tree_view):

        self.tree_view = tree_view

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

            self.tree_view.set_moving_note_mode(self.move_note)

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

    def rename_note(self, instance, new_name):

        if self.current_note != None:

            instance.dismiss()
            new_path = os.path.join(os.path.dirname(self.current_note.path), new_name + '.md')

            if not os.path.isfile(new_path):

                # Deselect the note
                self.note_view.deactivate_note()

                # Move the file
                move(self.current_note.path, new_path)

                # Refresh tree
                self.tree_view.folder_opened_without_touch(self.tree_view.active_node)

                # Reindex the note
                reindex_one_moved_note(self.hobbes_db, '.text_index', self.current_note.path, new_path)

                self.current_note = None

            else:
 
                info = InfoPopup(title="Renaming note", message="ERROR: Note already exists", size_hint=(.3, .2))
                info.open()

    def move_note(self, new_path):

        # Here I need to check all the notes and fix their relative paths to the attachments
        if self.current_note != None:

            # Add the filename to the new path
            new_path = os.path.join(new_path, os.path.basename(self.current_note.path))

            if not os.path.isfile(new_path):
 
                 # Deselect the note
                self.note_view.deactivate_note()

                # First fix note consistency
                fix_note_consistency(self.current_note.path, new_path, self.hobbes_db)
 
                # Then move the file
                move(self.current_note.path, new_path)
 
                # Refresh tree
                self.tree_view.folder_opened_without_touch(self.tree_view.active_node)

                # Reindex the note
                reindex_one_moved_note(self.hobbes_db, '.text_index', self.current_note.path, new_path)

                self.current_note = None
            else:
 
                info = InfoPopup(title="Moving note", message="ERROR: Note already exists", size_hint=(.3, .2))
                info.open()

    def delete_note(self, instance):

        instance.dismiss()

        if self.current_note != None:

            # Deselect the note
            self.note_view.deactivate_note()

            # Remove the file
            os.remove(self.current_note.path)

            # Refresh tree
            self.tree_view.folder_opened_without_touch(self.tree_view.active_node)

            # Delete from index
            del_doc(self.hobbes_db, '.text_index', self.current_note.path)

            self.current_note = None

    def import_note_to_pdf(self, in_path, out_path):

        # This imports are expensive, that is why they are not loaded on start
        from weasyprint import HTML

        html = markdown(self.note_text_input.text, output_format='html4')

        html = HTML(string=html)
        html.write_pdf('/tmp/example.pdf')