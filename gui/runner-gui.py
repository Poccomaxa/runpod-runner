import json

import TextSlider
import FloatText

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

class StyledBoxLayout(BoxLayout):
    pass

class RunnerGui(Screen):
    pass

class Logs(Screen):
    pass

class GenerationPanel(StyledBoxLayout):
    cfg_slider = ObjectProperty(None)
    steps_slider = ObjectProperty(None)
    text_prompt = ObjectProperty(None)
    text_negative_prompt = ObjectProperty(None)

    def on_generate_press(self):
        prompt_data = {
            "prompt": self.text_prompt.text,
            "negative_prompt": self.text_negative_prompt.text,
            "steps": f"{self.steps_slider.value:.3g}",
            "cfg_scale": f"{self.cfg_slider.value:.3g}",
            "width": "",
            "height": "",
            "enable_hr": False,
            "hr_scale": "",
            "hr_upscale": "",
            "hr_negative_prompt":"",
            "denoising_strength": 0.5,
            "batch_size": 1,
            "sampler_name": "Euler a"
        }

        print(json.dumps(prompt_data, indent=4))

class AppRoot(ScreenManager):
    pass

class RunnerGuiApp(App):
    sm = None
    def build(self):
        Window.bind(on_key_down=self.on_key_down)

        sm = AppRoot()
        sm.current = "Runner gui screen"
        return sm

    def on_key_down(self, window, key, scancode, action, mods):
        pass

if __name__ == '__main__':
    Window.size = (1440, 960)
    RunnerGuiApp().run()
