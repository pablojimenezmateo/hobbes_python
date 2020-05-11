from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color

import re
import os

# To open URLs when clicked 
import webbrowser

# To open files when clicked
import subprocess
import platform

NOTE_RENDERER_BACKGROUND_COLOR = (1, 1, 1, 1)
NOTE_RENDERER_UNDERLINE_COLOR = '000000FF'
NOTE_RENDERER_FONT_SIZE = 24

class NoteTextRenderer(ScrollView): 

    def __init__(self, **kwargs):
        super(NoteTextRenderer, self).__init__(**kwargs)

        self.label = self.ids.label

        # Format options
        self.label.padding = (16, 15)
        self.label.font_size = NOTE_RENDERER_FONT_SIZE

        #Listen for hiperlinks
        self.label.bind(on_ref_press=self.reference_click)

        # Stored images
        self.images = {}

        # This dirty hack is to avoid a bug
        # that would cause the bind [self.bind(width=self.resize_width)] to be called on loop
        # Just check if the Window has been resized
        self.prev_width = self.width

        self.images_need_rerender = False
        self.is_new_note = False

        # We need to keep an eye to re render the images
        Clock.schedule_interval(self.render_images, 0.1)

        self.original_text = ''

        self.current_note_path = ''

    def deactivate_note(self):

        self.current_note_path = None
        self.images_need_rerender = False
        self.label.text = ''
        self.is_new_note = False

    def on_new_note_open(self, current_note_path, text):

        self.current_note_path = current_note_path

        for path, w in self.images.items():

            self.label.remove_widget(w)

        self.images = {}

        self.is_new_note = True

        self.set_text(current_note_path, text)


    def set_text(self, current_note_path, text):

        self.original_text = text

        self.images_need_rerender = True

        self.current_note_path = current_note_path

        # First parse the text for links
        link_re = re.compile(r'^!?\[(local[^\]]+)\]\(([^)]+)\)$', flags=re.MULTILINE)

        # Load all the images
        for ind, match in enumerate(link_re.findall(text)):

            # Convert attachment links correctly
            # We need to get the relative path, translate it to an absolute path
            # and then add it to an [anchor] tag

            # Get the absolute path of the attachment from the relative path
            saved_path = os.getcwd()
            os.chdir(os.path.split(current_note_path)[0]) 
            abs_attachment_path = os.path.abspath(match[1])
            os.chdir(saved_path)

            if match[0] == 'local_image':

                if abs_attachment_path not in self.images:

                    wimg = Image(source=abs_attachment_path)
                    self.label.add_widget(wimg)
                    self.images[abs_attachment_path] = wimg

                    print("Loading", abs_attachment_path)

                self.original_text = self.original_text.replace('![local_image](' + match[1] + ')', '[anchor=' + abs_attachment_path + '].')

        # Get the absolute path with os.path.abspath(rel_path)
        if self.is_new_note:

            self.label.text = self.original_text
            self.is_new_note = False

    # This function handles when a [ref] is clicked
    def reference_click(self, instance, value):

        # Check if text is valid URL (https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not)
        url_regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(url_regex, value) is not None:

            webbrowser.open(value)
            return

        # It is a file
        if 'code_block_hobbes' not in value:

            # Get the absolute path of the attachment from the relative path
            saved_path = os.getcwd()
            os.chdir(os.path.split(self.current_note_path)[0]) 
            abs_attachment_path = os.path.abspath(value)
            os.chdir(saved_path)
            
            if platform.system() == 'Darwin':       # macOS

                subprocess.call(('open', abs_attachment_path))
            elif platform.system() == 'Windows':    # Windows

                os.startfile(abs_attachment_path)
            else:                                   # linux variants
                subprocess.call(('xdg-open', abs_attachment_path))

    def render_images(self, dt):

        # If the width has changed
        if self.prev_width != self.width:
            self.images_need_rerender = True

            self.prev_width = self.width

        if self.images_need_rerender:

            self.images_need_rerender = False

            # First modify the text
            aux_text = self.original_text

            for name, anc in self.label.anchors.items():

                i = self.images[name]

                i.width = self.width - 32
                i.height = self.width/i.image_ratio

                # After adding the image, I need to add enough whitespaces on that position so that the image does not cover the text
                vspace = round(i.height / (NOTE_RENDERER_FONT_SIZE + 4)) # That 4 is for intelining spacing

                aux_text = aux_text.replace('[anchor=' + name + '].', '\n'*vspace + '[anchor=' + name + ']')


            # Partial translation to kivy Markdown
            # Code blocks
            aux_text = re.sub(r'\`{3}(\s*[a-z]*\s*)([^\`]+)\`{3}', "[ref=code_block_hobbes][font=media/fonts/FiraCode-Regular.ttf]\\2[/font][/ref]", aux_text)

            # Links
            aux_text = re.sub(r"\[(.*?)\]\((.*?)\)", "[u][color=#0000EE][ref=\\2]\\1[/ref][/color][/u]", aux_text)

            # Bold
            aux_text = re.sub(r"\B([*_]{2})\b(.+?)\1\B", "[b]\\2[/b]", aux_text)

            # Italic
            aux_text = re.sub(r"\B([*_])\b(.+?)\1\B", "[i]\\2[/i]", aux_text)

            # Titles
            aux_text = re.sub(r"(?m)^#####\s+(.*?)\s*#*$", "[size=40][b]\\1[/b][/size]", aux_text)
            aux_text = re.sub(r"(?m)^####\s+(.*?)\s*#*$",  "[size=50][b]\\1[/b][/size]", aux_text)
            aux_text = re.sub(r"(?m)^###\s+(.*?)\s*#*$",   "[size=60][b]\\1[/b][/size]", aux_text)
            aux_text = re.sub(r"(?m)^##\s+(.*?)\s*#*$",    "[size=70][b]\\1[/b][/size]", aux_text)
            aux_text = re.sub(r"(?m)^#\s+(.*?)\s*#*$",     "[size=80][b]\\1[/b][/size]", aux_text)

            self.label.text = aux_text

            # We need to do this one tick after the label has rendered
            Clock.schedule_once(self.draw_backgrounds)
            Clock.schedule_once(self.move_images)

    def move_images(self, dt):

        # Then position the images
        for name, anc in self.label.anchors.items():

            i = self.images[name]
            i.pos = (16, self.label.texture_size[1] - self.label.anchors[name][1])

    # This functions are used to add a background to the special blocks
    @staticmethod
    def get_x(label, ref_x):
        """ Return the x value of the ref/anchor relative to the canvas """
        return label.center_x - label.texture_size[0] * 0.5 + ref_x

    @staticmethod
    def get_y(label, ref_y):
        """ Return the y value of the ref/anchor relative to the canvas """
        # Note the inversion of direction, as y values start at the top of
        # the texture and increase downwards
        return label.center_y + label.texture_size[1] * 0.5 - ref_y

    def draw_backgrounds(self, dt):

        label = self.label
        label.canvas.remove_group('code_background')

        # Draw a green surround around the refs. Note the sizes y inversion
        for name, boxes in label.refs.items():

            if 'code_block_hobbes' in name:
                for box in boxes:
                    with label.canvas:
                        Color(0, 0, 0, 0.15)
                        Rectangle(pos=(self.get_x(label, box[0]),
                                       self.get_y(label, box[1])),
                                  size=(self.width - 32,
                                        box[1] - box[3]), group='code_background')
