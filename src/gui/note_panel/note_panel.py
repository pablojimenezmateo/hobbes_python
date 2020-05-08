from kivy.uix.boxlayout import BoxLayout

# For the attachments
import hashlib
from shutil import copyfile

from src.gui.note_panel.note_text_input import *
from src.gui.note_panel.note_text_renderer import *

'''
    Combination of the text editor and renderer, I write my notes in Markdown
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

