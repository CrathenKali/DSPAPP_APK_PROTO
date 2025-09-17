
# frontend_kivy_control.py - Kivy UI with Unix Domain Socket client for DSP control
import os, json, socket, threading, time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.metrics import dp

KV_PATH = os.path.join(os.path.dirname(__file__), 'frontend_kivy.kv')
Builder.load_file(KV_PATH)

UDS_PATH = "@dsp_service_socket"  # LocalServerSocket name used by Java (same UDS_NAME)

class DSPControlClient:
    def __init__(self, uds_name=UDS_PATH):
        self.uds_name = uds_name

    def send(self, obj, timeout=1.0):
        """Send JSON obj over Android LocalSocket by connecting to the named server.
        On Android, using AF_UNIX abstract namespace requires special handling; however,
        Python's socket module supports AF_UNIX but abstract namespace (name starting with '\\0')
        is not directly representable. In many Python environments, connect to path '/data/local/tmp/...' works.
        Here we'll attempt to connect to a filesystem socket fallback path first, then abstract name."""
        msg = json.dumps(obj)
        # try filesystem socket path
        paths = ["/data/local/tmp/dsp_service.sock", self.uds_name]
        for p in paths:
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.settimeout(timeout)
                s.connect(p)
                s.sendall(msg.encode('utf-8'))
                # read ack
                try:
                    data = s.recv(1024)
                    if data:
                        return data.decode('utf-8')
                except Exception:
                    pass
                s.close()
                return None
            except Exception as e:
                # try next
                continue
        raise ConnectionError("Could not connect to UDS at known paths")

class DSPRoot(BoxLayout):
    pass

class FrontendApp(App):
    title = "DSP Headunit (Kivy)"
    def build(self):
        self.eq = [0.0]*31
        self.client = DSPControlClient()
        return DSPRoot()

    def on_eq_change(self, index, value):
        self.eq[index] = value
        # send to service
        try:
            self.client.send({"cmd":"eq","band":index,"value":value})
        except Exception as e:
            print("Control send error:", e)

    def on_input_mode(self, mode):
        try:
            self.client.send({"cmd":"input","mode":mode})
        except Exception as e:
            print("Control send error:", e)

    def on_gain(self, value):
        try:
            self.client.send({"cmd":"gain","value":value})
        except Exception as e:
            print("Control send error:", e)

    def on_delay(self, value):
        try:
            self.client.send({"cmd":"delay","value":value})
        except Exception as e:
            print("Control send error:", e)

    def select_channel(self, channel):
        try:
            self.client.send({"cmd":"select_channel","channel":channel})
        except Exception as e:
            print("Control send error:", e)

    def open_presets(self):
        # list presets in /sdcard/dsp_presets
        pdir = "/sdcard/dsp_presets"
        try:
            items = os.listdir(pdir)
            print("Presets:", items)
        except Exception:
            print("No presets directory:", pdir)

    def save_config(self):
        cfg = {"eq": self.eq}
        # save locally and also write preset file to /sdcard for DSP to load
        try:
            os.makedirs("/sdcard/dsp_presets", exist_ok=True)
            fname = "/sdcard/dsp_presets/preset_manual.json"
            with open(fname, "w") as fh:
                json.dump(cfg, fh)
            # notify service
            self.client.send({"cmd":"load_preset_file","path":fname})
            print("Saved config to", fname)
        except Exception as e:
            print("Save error:", e)

    def start_spectrum(self):
        # request service to start spectrum capture
        try:
            self.client.send({"cmd":"spectrum_start","path":"/sdcard/dsp_spectrum/spectrum_capture.json"})
            print("Requested spectrum start")
        except Exception as e:
            print("Spectrum start error:", e)

    def stop_spectrum(self):
        try:
            self.client.send({"cmd":"spectrum_stop"})
            print("Requested spectrum stop")
        except Exception as e:
            print("Spectrum stop error:", e)

if __name__ == '__main__':
    FrontendApp().run()
