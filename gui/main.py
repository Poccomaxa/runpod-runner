import json
import os
import asyncio
import sys

#Hack to stop windows from upscaling UI more than needed
if sys.platform == 'win32':
    try:
        from ctypes import windll, c_int64
        windll.user32.SetProcessDpiAwarenessContext(c_int64(-2))
    except (ImportError, AttributeError, OSError):
        pass

from kivy import Config
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.window import Keyboard

from common_popup import CommonPopup

# These imports are not used in file, but needed because of kivy reflection code that automatically injects classes when creating UI based on kv files
from generation import GenerationPanel  # noqa
from text_slider import TextSlider  # noqa
from float_text import FloatText  # noqa
from preview import Preview  # noqa
from prompts import PromptsPanel  # noqa
from settings import GlobalSettingsPanel  # noqa


class MainScreen(Screen):
    generation_panel = ObjectProperty(None)
    preview_panel = ObjectProperty(None)
    prompts_panel = ObjectProperty(None)
    tabbed_panel = ObjectProperty(None)
    global_settings_panel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self.prompts_panel.bind(on_load_requested=self.on_load_requested)
        self.prompts_panel.bind(on_save_requested=self.on_save_requested)
        self.preview_panel.bind(on_load_prompt_from_image=self.on_load_prompt_from_image)

    def on_load_requested(self, widget, filename: str):
        self.generation_panel.load_from_file(filename)
        self.tabbed_panel.switch_to(self.tabbed_panel.tab_list[2])

    def on_save_requested(self, widget, filename: str):
        self.generation_panel.save_to_file(filename)
        self.tabbed_panel.switch_to(self.tabbed_panel.tab_list[2])

    def on_load_prompt_from_image(self, widget, image_path):
        self.generation_panel.load_from_image_metadata(image_path)


class LogsScreen(Screen):
    logs = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.log_lines = []
        self.max_lines = 100
        super().__init__(**kwargs)

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


class AppRoot(ScreenManager):
    main_screen = ObjectProperty(None)
    logs_screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_screen_index = 0
        self.generation_exec = None
        self.user_switched = False

    async def run_generation(self, endpoint):
        self.generation_exec = await asyncio.create_subprocess_exec(
            'python', 'run_and_produce_image.py', 'prompts/last_prompt.json.tmp', '-p', endpoint,
            cwd=os.path.abspath('..'),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)

        async for line in self.generation_exec.stdout:
            self.logs_screen.add_byte_line(line)

        self.on_generation_script_finished()

    def on_prompt_ready(self, widget, json_data):
        print('Prompt ready')
        print(json.dumps(json_data, indent=4))

        endpoint = self.main_screen.global_settings_panel.api_endpoint_text.text
        if endpoint == '':
            popup = CommonPopup(title='No api endpoint', auto_dismiss=False)
            popup.text = 'You should provide your api endpoint for the first run in the settings tab. Later it will load last one automatically'
            popup.open()
            return

        self.switch_to_logs()
        self.logs_screen.add_line('Starting generation script...')
        self.user_switched = False

        with open('../prompts/last_prompt.json.tmp', 'w') as prompt_file:
            json.dump(json_data, prompt_file, indent=4)

        asyncio.get_event_loop().create_task(self.run_generation(endpoint))

    def on_generation_script_finished(self):
        if not self.user_switched:
            self.switch_to_main()
        self.logs_screen.add_line('Generation script finished!')
        self.main_screen.preview_panel.reload_images()

    def on_cycle_screens(self):
        self.user_switched = True
        self.cycle_screens()

    def cycle_screens(self):
        self.switch_to_index((self.current_screen_index + 1) % len(self.screen_names))

    def switch_to_logs(self):
        self.switch_to_name('logs')

    def switch_to_main(self):
        self.switch_to_name('main')

    def switch_to_name(self, name: str):
        self.switch_to_index(self.screen_names.index(name))

    def switch_to_index(self, index: int):
        self.current_screen_index = index
        self.current = self.screen_names[self.current_screen_index]

    def on_kv_post(self, base_widget):
        self.main_screen.generation_panel.bind(on_prompt_ready=self.on_prompt_ready)


class MainApp(App):
    code_to_name = {v: k for k, v in Keyboard.keycodes.items()}

    def __init__(self, **kwargs):
        self.sm = None
        super().__init__(**kwargs)

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        self.sm = AppRoot()
        return self.sm

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if key not in MainApp.code_to_name:
            return
        if MainApp.code_to_name[key] == '`':
            self.sm.on_cycle_screens()
        if MainApp.code_to_name[key] == 'spacebar':
            self.sm.main_screen.preview_panel.reset_scale()


if __name__ == '__main__':
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    Config.set('kivy', 'exit_on_escape', '0')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(MainApp().async_run('asyncio'))
