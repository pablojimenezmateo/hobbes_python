from kivy.uix.slider import Slider

# For audio playing
from pygame import mixer

class MusicSlider(Slider):

    def __init__(self, **kwargs):
        super(MusicSlider, self).__init__(**kwargs)

        # Audio
        mixer.init()
        mixer.set_num_channels(1)
        self.rain = mixer.Sound("media/audio/rain.ogg")

    def on_touch_up(self, touch):

        if self.value > 0:

            # If the sound is not playing, start it
            if not mixer.get_busy():

                self.rain.play(loops=-1)

            self.rain.set_volume(self.value)

        else:

            self.rain.fadeout(2000)    

        return True