import json

from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from styles import BasePanelBG
from text_dropdown import TextDropdown  # noqa

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

class GenerationPanel(BoxLayout, BasePanelBG):
    cfg_slider = ObjectProperty(None)
    steps_slider = ObjectProperty(None)
    text_prompt = ObjectProperty(None)
    text_negative_prompt = ObjectProperty(None)
    width_text = ObjectProperty(None)
    height_text = ObjectProperty(None)
    highres_checkbox = ObjectProperty(None)
    sampler_button = ObjectProperty(None)
    upscaler_button = ObjectProperty(None)
    hrscale_text = ObjectProperty(None)
    denoising_slider = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self.sampler_button.set_items(sampling_methods)
        self.upscaler_button.set_items(upscaler_methods)
        self.register_event_type('on_prompt_ready')

    def on_prompt_ready(self, *args):
        pass

    def on_generate_press(self):
        prompt_data = {
            'prompt': self.text_prompt.text,
            'negative_prompt': self.text_negative_prompt.text,
            'steps': f'{self.steps_slider.value:.3g}',
            'cfg_scale': f'{self.cfg_slider.value:.3g}',
            'width': int(self.width_text.text),
            'height': int(self.height_text.text),
            'sampler_name': self.sampler_button.text,
            'batch_size': 1,

            'enable_hr': self.highres_checkbox.active,
            'hr_scale': self.hrscale_text.text,
            'hr_upscaler': self.upscaler_button.text,
            'hr_negative_prompt': '',
            'denoising_strength': self.denoising_slider.value
        }
        full_data = {
            'input': prompt_data
        }



        self.dispatch('on_prompt_ready', full_data)

    def load_from_file(self, filename: str):
        with open("../prompts/" + filename, 'rb') as prompt_file:
            data = json.load(prompt_file)
            self.load_from_json(data)

    def load_from_json(self, json_data):
        print(json_data)
        prompt_data = json_data['input']
        self.text_prompt.text = prompt_data.get('prompt', '')
        self.text_negative_prompt.text = prompt_data.get('negative_prompt', '')
        self.steps_slider.value = prompt_data.get('steps', 20)
        self.sampler_button.text = prompt_data.get('sampler_name', 'Euler a')
        self.cfg_slider.value = prompt_data.get('cfg_scale', 7)
        self.width_text.text = str(prompt_data.get('width', 1024))
        self.height_text.text = str(prompt_data.get('height',768))

        self.highres_checkbox.active = prompt_data.get('enable_hr', False)
        self.hrscale_text.text = str(prompt_data.get('hr_scale', 2))
        self.upscaler_button.text = prompt_data.get('hr_upscaler', 'None')
        self.denoising_slider.value = prompt_data.get('denoising_strength', 0.5)
        pass
