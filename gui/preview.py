import os

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

def lerp(a: float, b: float, t: float) -> float:
    return (1 - t) * a + t * b

def align_in_frame(cnt_min: float, cnt_max: float, img_min: float, img_max: float) -> float:
    img_size = img_max - img_min
    cnt_size = cnt_max - cnt_min

    desired_delta = 0
    if cnt_size > img_size:
        desired_delta = (cnt_max + cnt_min - img_max - img_min) / 2
    elif img_min > cnt_min:
        desired_delta = cnt_min - img_min
    elif img_max < cnt_max:
        desired_delta = cnt_max - img_max

    return desired_delta


class Thumbnail(ButtonBehavior, BoxLayout):
    file_name = ObjectProperty(None)
    image_thumb = ObjectProperty(None)

    def on_press(self):
        pass


class Preview(BoxLayout):
    file_list = ObjectProperty(None)
    big_image = ObjectProperty(None)
    scatter_container = ObjectProperty(None)
    image_panel = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        Clock.schedule_interval(self.on_update, 0)
        if os.path.exists('../output'):
            image_paths = os.listdir('../output')
            for imagePath in image_paths:
                new_thumbnail = Thumbnail()
                new_thumbnail.file_name.text = imagePath
                new_thumbnail.image_thumb.source = "../output/" + imagePath
                new_thumbnail.bind(on_press=self.on_image_selected)
                self.file_list.add_widget(new_thumbnail)

    def on_image_selected(self, widget):
        self.scatter_container.scale = 1
        self.scatter_container.pos = self.scatter_container.to_parent(0, 0)
        self.scatter_container.rotation = 0

        self.big_image.source = widget.image_thumb.source

    def reset_scale(self):
        self.scatter_container.scale = 1

    def on_touch_down(self, touch):
        if self.image_panel.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                scale_delta = -1 if touch.button == 'scrollup' else 1
                scale_delta = 1 + scale_delta * 0.1
                self.scatter_container.scale = max(0.1, min(self.scatter_container.scale * scale_delta, 10))
                return True
        return super().on_touch_down(touch)

    def on_update(self, dt):
        cnt_min_point = (0, 0)
        cnt_max_point = self.image_panel.size

        img_min_point = self.scatter_container.to_parent(0, 0)
        img_min_point = self.image_panel.to_local(*img_min_point, True)

        img_max_point = self.scatter_container.to_parent(*self.scatter_container.size)
        img_max_point = self.image_panel.to_local(*img_max_point, True)

        desired_delta = (align_in_frame(cnt_min_point[0], cnt_max_point[0], img_min_point[0], img_max_point[0]),
                         align_in_frame(cnt_min_point[1], cnt_max_point[1], img_min_point[1], img_max_point[1]))

        actual_delta = (lerp(img_min_point[0], img_min_point[0] + desired_delta[0], 0.5),
                        lerp(img_min_point[1], img_min_point[1] + desired_delta[1], 0.5))

        self.scatter_container.pos = self.image_panel.to_parent(*actual_delta, True)
