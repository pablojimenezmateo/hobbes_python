from kivy.uix.button import Button

'''
    Each of the options
'''
class ContextButton(Button):

    def __init__(self, **kwargs):
        super(ContextButton, self).__init__(**kwargs)

        self.background_normal = 'media/images/button_bckgnd.png'
        self.background_down = ''
        self.background_color = (1, 1, 1, 1)
        self.color = (0, 0, 0, 1)            # Text color