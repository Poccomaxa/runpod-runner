import json

import text_slider
import float_text

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.window import Keyboard

class MainScreen(Screen):
    pass

class LogsScreen(Screen):
    pass

class StyledBoxLayout(BoxLayout):
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
    current_screen_index = 0

    def cycle_screens(self):
        self.current_screen_index = (self.current_screen_index + 1) % len(self.screen_names)
        self.current = self.screen_names[self.current_screen_index]

class MainApp(App):
    sm = None
    code_to_name = {v: k for k, v in Keyboard.keycodes.items()}

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        self.sm = AppRoot()
        return self.sm

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.code_to_name[key] == "`":
            self.sm.cycle_screens()

if __name__ == "__main__":
    Window.size = (1440, 960)
    MainApp().run()
