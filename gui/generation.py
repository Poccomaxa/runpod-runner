import json

from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label

from styles import BasePanelBG

sampling_methods = [
    'DPM++ 2M',
    'DPM++ SDE',
    'DPM++ 2M SDE',
    'DPM++ 2M SDE Heun',
    'DPM++ 2S a',
    'DPM++ 3M SDE',
    'Euler a',
    'Euler',
    'LMS',
    'Heun',
    'DPM2',
    'DPM2 a',
    'DPM fast',
    'DPM adaptive',
    'Restart'
]

upscaler_methods = [
    'Latent',
    'Latent (antialiased)',
    'Latent (bicubic)',
    'Latent (bicubic antialiased)',
    'Latent (nearest)',
    'Latent (nearest-exact)',
    'None',
    'Lanczos',
    'Nearest'
]

class DropDownLine(ButtonBehavior, Label):
    pass

class DropDownPanel(BoxLayout, BasePanelBG):
    pass

class GenerationPanel(BoxLayout, BasePanelBG):
    cfg_slider = ObjectProperty(None)
    steps_slider = ObjectProperty(None)
    text_prompt = ObjectProperty(None)
    text_negative_prompt = ObjectProperty(None)
    width_text = ObjectProperty(None)
    height_text = ObjectProperty(None)
    highres_checkbox = ObjectProperty(None)
    sampler_button = ObjectProperty(None)
    sampler_container = None
    sampler_dropdown = None

    def on_kv_post(self, base_widget):
        self.sampler_container = DropDownPanel()
        self.sampler_dropdown = DropDown()
        for sampling_method in sampling_methods:
            new_entry = DropDownLine(
                text=sampling_method
            )
            self.sampler_container.add_widget(new_entry)

        self.sampler_dropdown.add_widget(self.sampler_container)
        self.sampler_button.bind(on_press=self.sampler_dropdown.open)
        self.register_event_type('on_prompt_ready')

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
            'hr_upscaler': '',
            'hr_negative_prompt': '',
            'denoising_strength': 0.5,
            'batch_size': 1,
            'sampler_name': 'Euler a'
        }
        full_data = {
            'input': prompt_data
        }

        print(json.dumps(full_data, indent=4))

        self.dispatch('on_prompt_ready')



    def load_from_file(self, filename: str):
        with open("../prompts/" + filename, 'rb') as prompt_file:
            data = json.load(prompt_file)
            self.load_from_json(data)

    def load_from_json(self, json_data):
        print(json_data)
        prompt_data = json_data['input']
        self.text_prompt.text = prompt_data['prompt']
        self.text_negative_prompt.text = prompt_data['negative_prompt']
        self.steps_slider.value = prompt_data['steps']
        self.cfg_slider.value = prompt_data['cfg_scale']
        self.width_text.text = str(prompt_data['width'])
        self.height_text.text = str(prompt_data['height'])
        self.highres_checkbox.active = prompt_data['enable_hr']
        pass
