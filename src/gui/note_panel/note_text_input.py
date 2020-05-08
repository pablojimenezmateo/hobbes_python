from kivy.uix.textinput import TextInput

NOTE_INPUT_FONT_SIZE = 24

'''
    This will be used to edit notes
'''
class NoteTextInput(TextInput):

    def __init__(self, **kwargs):
        super(NoteTextInput, self).__init__(**kwargs)

        self.font_size = NOTE_INPUT_FONT_SIZE
        self.background_normal = ''
        self.padding = [16, 15, 6, 6]