from kivy.uix.popup import Popup
from kivy.uix.label import Label


'''
    Generic info popup
'''

class InfoPopup(Popup):

    def __init__(self, message, **kwargs):

        super(InfoPopup, self).__init__(**kwargs)

        self.add_widget(Label(text=message))
