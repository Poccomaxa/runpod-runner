import re

from kivy.properties import BooleanProperty
from kivy.uix.textinput import TextInput


class FloatText(TextInput):
    allow_decimal = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text or not self.allow_decimal:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join(
                re.sub(pat, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, from_undo=from_undo)
    pass
