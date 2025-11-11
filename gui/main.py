import json
import os
import re
import asyncio

from kivy.uix.label import Label
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.window import Keyboard

from gui.styles import BasePanelBG
from gui.preview import Preview, Thumbnail
from gui.text_slider import TextSlider


class MainScreen(Screen):
    generation_panel = ObjectProperty(None)
    preview_panel = ObjectProperty(None)


class LogsScreen(Screen):
    logs = ObjectProperty(None)
    log_lines = []
    max_lines = 100

    def add_byte_line(self, line_bytes):
        line = line_bytes.decode('utf-8')
        self.add_line(line)

    def add_line(self, line):
        line = line.replace('\n', '')
        line = line.replace('\r', '')
        line = '> ' + line
        self.log_lines.append(line)
        self.log_lines = self.log_lines[-self.max_lines:]
        self.logs.text = '\n'.join(self.log_lines)


class PromptsItem(Label):
    pass


class PromptsPanel(BoxLayout):
    prompt_list = ObjectProperty(None)
    print(prompt_list, "prompts")

    def load_prompts(self):
        files = os.listdir('../prompts')
        pat = re.compile('.*\.json')
        self.prompt_list.clear_widgets()
        for file in files:
            if pat.fullmatch(file):
                new_label = PromptsItem(text=file)

                self.prompt_list.add_widget(new_label)

    def on_parent(self, widget, parent):
        self.load_prompts()


class GenerationPanel(BoxLayout, BasePanelBG):
    cfg_slider = ObjectProperty(None)
    steps_slider = ObjectProperty(None)
    text_prompt = ObjectProperty(None)
    text_negative_prompt = ObjectProperty(None)

    def on_prompt_ready(self, *args):
        pass

    def on_generate_press(self):
        prompt_data = {
            'prompt': self.text_prompt.text,
            'negative_prompt': self.text_negative_prompt.text,
            'steps': f'{self.steps_slider.value:.3g}',
            'cfg_scale': f'{self.cfg_slider.value:.3g}',
            'width': '',
            'height': '',
            'enable_hr': False,
            'hr_scale': '',
            'hr_upscale': '',
            'hr_negative_prompt': '',
            'denoising_strength': 0.5,
            'batch_size': 1,
            'sampler_name': 'Euler a'
        }

        print(json.dumps(prompt_data, indent=4))

        self.dispatch('on_prompt_ready')

    def on_parent(self, widget, parent):
        self.register_event_type('on_prompt_ready')


class AppRoot(ScreenManager):
    current_screen_index = 0
    main_screen = ObjectProperty(None)
    logs_screen = ObjectProperty(None)
    generation_exec = None
    user_switched = False

    async def run_generation(self):
        self.generation_exec = await asyncio.create_subprocess_exec(
            'python', 'run_and_produce_image.py', '-h', cwd=os.path.abspath('..'),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)

        async for line in self.generation_exec.stdout:
            self.logs_screen.add_byte_line(line)

        self.on_generation_script_finished()

    def on_prompt_ready(self, *args):
        self.switch_to_logs()
        self.logs_screen.add_line('Starting generation script...')
        self.user_switched = False
        asyncio.get_event_loop().create_task(self.run_generation())

    def on_generation_script_finished(self):
        if not self.user_switched:
            self.switch_to_main()
        self.logs_screen.add_line('Generation script finished!')

    def on_cycle_screens(self):
        self.user_switched = True
        self.cycle_screens()

    def cycle_screens(self):
        self.current_screen_index = (self.current_screen_index + 1) % len(self.screen_names)
        self.current = self.screen_names[self.current_screen_index]

    def switch_to_logs(self):
        self.current = 'logs'

    def switch_to_main(self):
        self.current = 'main'

    def on_parent(self, widget, parent):
        self.main_screen.generation_panel.bind(on_prompt_ready=self.on_prompt_ready)


class MainApp(App):
    sm = None
    code_to_name = {v: k for k, v in Keyboard.keycodes.items()}

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        self.sm = AppRoot()
        return self.sm

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.code_to_name[key] == '`':
            self.sm.on_cycle_screens()
        if self.code_to_name[key] == 'spacebar':
            self.sm.main_screen.preview_panel.reset_scale()


if __name__ == '__main__':
    # Config.set('input', 'mouse', 'mouse,disable_multitouch')

    Window.top = 100
    Window.left = 1950
    Window.size = (1440, 960)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(MainApp().async_run('asyncio'))
