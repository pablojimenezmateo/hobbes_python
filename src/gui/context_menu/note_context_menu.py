from src.gui.popup.info_popup import *
from src.gui.popup.textinput_popup import *
from src.gui.popup.confirmation_popup import *

from markdown import markdown

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
        export_note_button   = Button(text="Export note to PDF")
        self.context_menu.add_widget(rename_note_button)
        self.context_menu.add_widget(move_note_button)
        self.context_menu.add_widget(delete_note_button)
        self.context_menu.add_widget(export_note_button)

        # Bind the buttons to functions
        rename_note_button.bind(on_release = self.rename_note_popup) 
        move_note_button.bind(on_release = self.move_note_popup)
        delete_note_button.bind(on_release = self.delete_note_popup)
        export_note_button.bind(on_release = self.export_note_popup)

        self.content = self.context_menu

        self.current_note = None

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

    def rename_note(self, *l):

        # Here I need to check all the notes and fix their relative paths to the attachments

        if self.current_note != None:

            print("Rename note", self.current_note.text)

    def move_note(self, *l):

        # Here I need to check all the notes and fix their relative paths to the attachments

        if self.current_note != None:

            print("Move note", self.current_note.text)

    def delete_note(self, *l):

        if self.current_note != None:

            print("Delete note", self.current_note.text)

    def import_note_to_pdf(self, in_path, out_path):

        # This imports are expensive, that is why they are not loaded on start
        from weasyprint import HTML

        html = markdown(self.note_text_input.text, output_format='html4')

        html = HTML(string=html)
        html.write_pdf('/tmp/example.pdf')