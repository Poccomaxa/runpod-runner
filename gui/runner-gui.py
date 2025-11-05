import re

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput


class FloatText(TextInput):
    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join(
                re.sub(pat, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, from_undo=from_undo)
    pass

class TextSlider(BoxLayout):
    text_input = ObjectProperty(None)
    pass

class StyledBoxLayout(BoxLayout):
    pass

class RunnerGui(AnchorLayout):
    pass

class GenerationGui(StyledBoxLayout):
    pass

class RunnerGuiApp(App):
    def build(self):
        return RunnerGui()

if __name__ == '__main__':
    RunnerGuiApp().run()