from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button

'''
    Generic confirmation dialog
'''
class ConfirmPopup(Popup):

    def __init__(self, message, callback, **kwargs):

        super(ConfirmPopup, self).__init__(**kwargs)

        layout_top = BoxLayout(orientation='vertical', size_hint=(1, .5))
        layout_top.add_widget(Label(text=message, size_hint=(1, .5)), 1)

        layout_bottom = BoxLayout(orientation='horizontal', size_hint=(1, .5))

        self.confirm_button = Button(text='Confirm', size_hint=(.5, 1))
        layout_bottom.add_widget(self.confirm_button)
        self.cancel_button = Button(text='Cancel', size_hint=(.5, 1))
        layout_bottom.add_widget(self.cancel_button)
        layout_top.add_widget(layout_bottom)

        self.add_widget(layout_top)

        # If the cancel button is pressed, just close the popup
        self.confirm_button.bind(on_release=self.my_callback)
        self.cancel_button.bind(on_release=self.dismiss)

        self.callback = callback

    def my_callback(self, l):

        self.callback(self)

    # Set the focus when opened
    def on_open(self):

        self.confirm_button.focus = True