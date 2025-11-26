import json
from pathlib import Path

from PIL import Image, PngImagePlugin

from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from common_popup import CommonPopup
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


def to_int(string: str, default):
    try:
        return int(string)
    except ValueError:
        return default


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
    batch_text = ObjectProperty(None)
    seed_text = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self.sampler_button.set_items(sampling_methods)
        self.upscaler_button.set_items(upscaler_methods)
        self.register_event_type('on_prompt_ready')

    def on_prompt_ready(self, *args):
        pass

    def generate_prompt_data(self):
        prompt_data = {
            'prompt': self.text_prompt.text,
            'negative_prompt': self.text_negative_prompt.text,
            'steps': f'{self.steps_slider.value:.3g}',
            'cfg_scale': f'{self.cfg_slider.value:.3g}',
            'width': to_int(self.width_text.text, 512),
            'height': to_int(self.height_text.text, 512),
            'sampler_name': self.sampler_button.text,
            'batch_size': to_int(self.batch_text.text, 1),
        }

        if self.highres_checkbox.active:
            prompt_data['enable_hr'] = True
            prompt_data['hr_upscaler'] = self.upscaler_button.text
            # TODO
            prompt_data['hr_negative_prompt'] = ''
            prompt_data['denoising_strength'] = self.denoising_slider.value
            prompt_data['hr_scale'] = self.hrscale_text.text if self.hrscale_text.text != '' else 1

        if self.seed_text.text != '':
            prompt_data['seed'] = self.seed_text.text

        full_data = {
            'input': prompt_data
        }
        return full_data

    def on_generate_press(self):
        self.dispatch('on_prompt_ready', self.generate_prompt_data())

    def load_from_image_metadata(self, filename: str):
        img = Image.open(filename)
        print(img.info['parameters'])
        sections = str.split(img.info['parameters'], '\n')

        self.text_prompt.text = sections[0]
        if sections[1].find('Negative prompt:') != -1:
            self.text_negative_prompt.text = sections[1].replace('Negative prompt:', '').strip()

        params_section = sections[-1]
        params = str.split(params_section, ',')
        steps = next((s for s in params if 'Steps:' in s), None)
        if steps is not None:
            self.steps_slider.value = float(steps.replace('Steps:', '').strip())

        sampler = next((s for s in params if 'Sampler:' in s), None)
        if sampler is not None:
            self.sampler_button.text = sampler.replace('Sampler:', '').strip()

        cfg_scale = next((s for s in params if 'CFG scale:' in s), None)
        if cfg_scale is not None:
            self.cfg_slider.value = float(cfg_scale.replace('CFG scale:', '').strip())

        seed = next((s for s in params if 'Seed:' in s), None)
        if seed is not None:
            self.seed_text.text = seed.replace('Seed:', '').strip()

        image_size = next((s for s in params if 'Size:' in s), None)
        if image_size is not None:
            image_size_dimensions = image_size.replace('Size:', '').strip().split('x')
            self.width_text.text = image_size_dimensions[0]
            self.height_text.text = image_size_dimensions[1]

    def load_from_file(self, filename: str):
        with open("../prompts/" + filename, 'rb') as prompt_file:
            data = json.load(prompt_file)
            self.load_from_json(data)

    def save_to_file(self, filename: str):
        full_path = '../prompts/' + filename + '.json'
        if Path(full_path).exists():
            popup = CommonPopup(title='Already exists', auto_dismiss=False)
            popup.text = 'This prompt filename is already in use, choose another'
            popup.open()
        else:
            with open(full_path, 'w') as prompt_file:
                full_json = self.generate_prompt_data()
                json.dump(full_json, prompt_file, indent=4)

    def load_from_json(self, json_data):
        prompt_data = json_data['input']
        self.text_prompt.text = prompt_data.get('prompt', '')
        self.text_negative_prompt.text = prompt_data.get('negative_prompt', '')
        self.steps_slider.value = prompt_data.get('steps', 20)
        self.sampler_button.text = prompt_data.get('sampler_name', 'Euler a')
        self.cfg_slider.value = prompt_data.get('cfg_scale', 7)
        self.width_text.text = str(prompt_data.get('width', 1024))
        self.height_text.text = str(prompt_data.get('height', 768))
        self.batch_text.text = str(prompt_data.get('batch_size', 1))

        self.highres_checkbox.active = prompt_data.get('enable_hr', False)
        self.hrscale_text.text = str(prompt_data.get('hr_scale', 2))
        self.upscaler_button.text = prompt_data.get('hr_upscaler', 'None')
        self.denoising_slider.value = prompt_data.get('denoising_strength', 0.5)
        self.seed_text.text = prompt_data.get('seed', '')
        pass
