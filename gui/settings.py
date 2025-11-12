import json

from kivy.properties import ObjectProperty
from kivy.uix.stacklayout import StackLayout

from styles import BasePanelBG

class GlobalSettingsPanel(StackLayout, BasePanelBG):
    api_endpoint_text = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        with open('../cache.json', 'r') as cache_file:
            cache_data = json.load(cache_file)
            self.api_endpoint_text.text = cache_data.get('endpoint', '')
