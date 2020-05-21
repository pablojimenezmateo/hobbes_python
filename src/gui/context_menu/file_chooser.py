from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.uix.filechooser import FileChooserListView
from src.gui.context_menu.context_button import *
from kivy.core.window import Window



import os

class SaveDialog(ModalView):

    _is_open = False

    def __init__(self, hobbes_db, **kwargs):
        super(SaveDialog, self).__init__(**kwargs)

        self.hobbes_db = hobbes_db
        file_chooser = FileChooserListView(dirselect=True, path=self.hobbes_db)

        self.add_widget(file_chooser)

        # Pay attention to keyboard events
        Window.bind(on_key_down=self.on_keyboard)

        self.bind(on_dismiss=self.on_custom_dismiss)

    def show_save(self):

        self._is_open = True
        self.open()

    def on_keyboard(self, window, key, scancode, codepoint, modifier):

        if self._is_open:

            print(window, key, scancode, codepoint, modifier)

    def on_custom_dismiss(self, value):

        self._is_open = False

#class FileChooser(FloatLayout):
#
#    
#
#    def dismiss_popup(self):
#        self._popup.dismiss()
#
#    def show_save(self):
#        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
#        self._popup = ModalView(size_hint=(0.9, 1))
#        self._popup.add_widget(content)
#        self._popup.open()
#
#    def save(self, path, filename):
#
#        print("Saving to ", os.path.join(path, filename))
#        self.dismiss_popup()
#
#Factory.register('SaveDialog', cls=SaveDialog)
#Factory.register('FileChooser', cls=SaveDialog)#