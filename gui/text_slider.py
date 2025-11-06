from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

class TextSlider(BoxLayout):
    text_input = ObjectProperty(None)
    slider = ObjectProperty(None)
    value = NumericProperty(0)
    min_value = NumericProperty(0)
    max_value = NumericProperty(0)
    changeGuard = False

    def on_slider_value(self, value):
        if not self.changeGuard:
            self.changeGuard = True
            self.text_input.text = f"{value:.3g}"
            self.value = value
            self.changeGuard = False

    def on_text_changed(self, text):
        try:
            if not self.changeGuard:
                self.changeGuard = True
                float_value = float(text)
                float_value_clamped = max(self.min_value, min(self.max_value, float_value))
                if float_value != float_value_clamped:
                    self.text_input.text = f"{float_value_clamped:.3g}"
                self.value = float_value_clamped
                self.changeGuard = False
        except Exception:
            self.changeGuard = False
