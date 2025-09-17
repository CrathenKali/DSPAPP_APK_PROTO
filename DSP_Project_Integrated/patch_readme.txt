
Patches applied:
- AudioService.java.patched2 includes a LocalServerSocket-based control server (UDS) and handlers for DSP commands.
  - Starts server on service init; listens for JSON commands from UI.
  - Adds handlers for eq, gain, input, delay, select_channel, load_preset_file, spectrum_start, spectrum_stop.
  - Logs to /sdcard/dsp_logs/control.log and writes presets to /sdcard/dsp_presets/.

- frontend_kivy_control.py is a Kivy UI variant that uses a Unix Domain Socket client to send JSON commands to the service.
  - Uses /data/local/tmp/dsp_service.sock or abstract name fallback.

Integration:
- Replace main.py with frontend_kivy_control.py (or import its DSPControlClient) to enable IPC.
- Ensure UDS name/path matches in both Java and Python sides.
- For production, implement native DSP in C++ and call via JNI from Java; Java service should route control commands to the native engine.

Next steps I can do:
- Implement native JNI stubs (C++ source) and build scripts (Android.mk/CMakeLists).
- Convert UDS server to filesystem socket at /data/local/tmp/dsp_service.sock (requires permission).
- Merge patches into your repo structure (src/main/java/...).
