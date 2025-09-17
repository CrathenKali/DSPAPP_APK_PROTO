from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
import json, os

KV_PATH = os.path.join(os.path.dirname(__file__), 'frontend_kivy.kv')
Builder.load_file(KV_PATH)

class DSPRoot(BoxLayout):
    pass

class FrontendApp(App):
    title = "DSP Headunit (Kivy)"
    def build(self):
        self.eq = [0.0]*31
        return DSPRoot()

    # UI callbacks
    def on_eq_change(self, index, value):
        self.eq[index] = value
        print(f"EQ band {index} -> {value} dB")
        # TODO: send to DSP core (audio_service) via pyjnius or IPC bridge

    def on_input_mode(self, mode):
        print("Input mode ->", mode)
        # TODO: call audio routing logic

    def on_gain(self, value):
        print("Master gain ->", value)

    def on_delay(self, value):
        print("Delay ->", value)

    def select_channel(self, channel):
        print("Select channel:", channel)

    def open_presets(self):
        print("Open presets")

    def save_config(self):
        cfg = {
            "eq": self.eq
        }
        with open('/sdcard/dsp_config.json','w') as fh:
            json.dump(cfg, fh)
        print("Saved config to /sdcard/dsp_config.json")

if __name__ == '__main__':
    FrontendApp().run()