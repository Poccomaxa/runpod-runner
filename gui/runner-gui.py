import re

from kivy.app import App
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput


class FloatText(TextInput):
    allow_decimal = BooleanProperty(False)

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

class TextSlider(BoxLayout):
    text_input = ObjectProperty(None)
    slider = ObjectProperty(None)
    value = NumericProperty(0)
    min_value = NumericProperty(0)
    max_value = NumericProperty(0)
    changeGuard = False

    def on_slider_value(self, value):
        if not self.changeGuard:
            self.changeGuard = True
            self.text_input.text = f"{value:.3g}"
            self.changeGuard = False

    def on_text_changed(self, text):
        try:
            if not self.changeGuard:
                self.changeGuard = True
                float_value = float(text)
                float_value_clamped = max(self.min_value, min(self.max_value, float_value))
                if float_value != float_value_clamped:
                    self.text_input.text = f"{float_value_clamped:.3g}"
                self.value = float_value_clamped
                self.changeGuard = False
        except Exception:
            self.changeGuard = False

class StyledBoxLayout(BoxLayout):
    pass

class RunnerGui(AnchorLayout):
    pass

class GenerationPanel(StyledBoxLayout):
    prompt_data = {}
    def on_cfgscale_changed(self, value):
        self.prompt_data["cfg_scale"] = value

    def on_steps_changed(self, value):
        self.prompt_data["steps"] = value
    pass

class RunnerGuiApp(App):
    def build(self):
        return RunnerGui()

if __name__ == '__main__':
    RunnerGuiApp().run()

    # "prompt": "",
    # "negative_prompt": "",
    # "steps": 20,
    # "cfg_scale": 4.5,
    # "width": 1280,
    # "height": 720,
    # "enable_hr": false,
    # "hr_scale":2,
    # "hr_upscaler":"Nearest",
    # "hr_negative_prompt":"text,watermark,signature,username",
    # "denoising_strength":0.5,
    # "batch_size": 1,
    # "sampler_name": "Euler a"