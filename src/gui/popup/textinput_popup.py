from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

'''
    Generic textinput popup
'''
class TextinputPopup(Popup):

    def __init__(self, message, callback, **kwargs):

        super(TextinputPopup, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        layout.add_widget(Label(text=message, size_hint=(1, .5)), 1)
        self.textinput = TextInput(text='', multiline=False, size_hint=(1, .5))

        layout.add_widget(self.textinput, 0)

        self.add_widget(layout)

        self.textinput.bind(on_text_validate=self.my_callback)

        self.callback = callback

    def my_callback(self, textinput):

        self.callback(self, textinput.text)

    # Set the focus when opened
    def on_open(self):

        self.textinput.focus = True