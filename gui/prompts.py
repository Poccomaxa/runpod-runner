import os
import re

from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class PromptsItem(ButtonBehavior, Label):
    selected = BooleanProperty(False)
    pass


class PromptsPanel(BoxLayout):
    prompt_list = ObjectProperty(None)
    selected_item = None

    def load_prompts(self):
        files = os.listdir('../prompts')
        pat = re.compile('.*\.json')
        self.prompt_list.clear_widgets()
        for file in files:
            if pat.fullmatch(file):
                new_label = PromptsItem(text=file)
                new_label.bind(on_press=self.on_prompt_selected)

                self.prompt_list.add_widget(new_label)

    def on_kv_post(self, base_widget):
        self.register_event_type('on_load_requested')
        self.load_prompts()

    def on_load_requested(self, to_load: str):
        pass

    def on_prompt_selected(self, widget):
        if self.selected_item is not None:
            self.selected_item.selected = False

        self.selected_item = widget
        self.selected_item.selected = True

    def on_load_pressed(self):
        if self.selected_item is not None:
            self.dispatch('on_load_requested', self.selected_item.text)
