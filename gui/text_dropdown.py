from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label

from styles import BasePanelBG


class DropDownLine(ButtonBehavior, Label):
    pass


class DropDownPanel(BoxLayout, BasePanelBG):
    pass


class TextDropdown(Button):
    def __init__(self, **kwargs):
        self.sampler_container = DropDownPanel()
        self.sampler_dropdown = DropDown()

        super().__init__(**kwargs)

    def set_items(self, items_list):
        for entry in items_list:
            new_entry = DropDownLine(
                text=entry
            )
            new_entry.bind(on_press=lambda element: self.sampler_dropdown.select(element.text))
            self.sampler_container.add_widget(new_entry)

        self.sampler_dropdown.add_widget(self.sampler_container)
        self.sampler_container.bind(width=lambda obj, value: setattr(self, 'width', value + 10))
        self.bind(on_press=self.sampler_dropdown.open)
        self.sampler_dropdown.bind(on_select=self.on_sampler_selected)

    def on_sampler_selected(self, widget, selection):
        self.text = selection
