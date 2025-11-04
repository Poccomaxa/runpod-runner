from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout


class RunnerGui(AnchorLayout):
    pass

class RunnerGuiApp(App):
    def build(self):
        return RunnerGui()

if __name__ == '__main__':
    RunnerGuiApp().run()