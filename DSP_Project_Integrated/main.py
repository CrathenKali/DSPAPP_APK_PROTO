#!/usr/bin/env python3
“””
Professional Car Audio DSP Application
Main application file for Android APK build
Handles external 3.5mm mic input for audio analysis and calls
“””

import kivy
kivy.require(‘2.1.0’)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

import numpy as np
import threading
import json
import time
from collections import deque

# Android-specific imports

if platform == ‘android’:
from jnius import autoclass, cast
from android.permissions import request_permissions, Permission
from android.runnable import run_on_ui_thread

```
# Android Audio classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
AudioManager = autoclass('android.media.AudioManager')
AudioRecord = autoclass('android.media.AudioRecord')
MediaRecorder = autoclass('android.media.MediaRecorder$AudioSource')
AudioFormat = autoclass('android.media.AudioFormat')
AudioTrack = autoclass('android.media.AudioTrack')
AudioAttributes = autoclass('android.media.AudioAttributes')

# Request permissions
request_permissions([
    Permission.RECORD_AUDIO,
    Permission.MODIFY_AUDIO_SETTINGS,
    Permission.WRITE_EXTERNAL_STORAGE,
    Permission.BLUETOOTH,
    Permission.WAKE_LOCK
])
```

class AudioProcessor:
“”“Real-time audio processing for external mic input”””

```
def __init__(self):
    self.sample_rate = 44100
    self.buffer_size = 4096
    self.is_recording = False
    self.audio_data = deque(maxlen=self.sample_rate * 2)  # 2 seconds of data
    self.fft_data = np.zeros(512)
    self.rms_level = 0.0
    self.peak_level = 0.0
    
    # Android audio objects
    self.audio_record = None
    self.audio_manager = None
    
    if platform == 'android':
        self.setup_android_audio()

def setup_android_audio(self):
    """Configure Android audio system for external mic"""
    try:
        activity = PythonActivity.mActivity
        self.audio_manager = activity.getSystemService(activity.AUDIO_SERVICE)
        
        # Force audio routing to external mic (3.5mm input)
        self.audio_manager.setMode(AudioManager.MODE_IN_COMMUNICATION)
        self.audio_manager.setSpeakerphoneOn(False)
        self.audio_manager.setWiredHeadsetOn(True)
        
        # Configure AudioRecord for external mic
        channel_config = AudioFormat.CHANNEL_IN_MONO
        audio_format = AudioFormat.ENCODING_PCM_16BIT
        
        # Try different audio sources to find external mic
        audio_sources = [
            MediaRecorder.MIC,
            MediaRecorder.VOICE_COMMUNICATION,
            MediaRecorder.VOICE_RECOGNITION,
            MediaRecorder.UNPROCESSED
        ]
        
        for source in audio_sources:
            try:
                min_buffer_size = AudioRecord.getMinBufferSize(
                    self.sample_rate, channel_config, audio_format
                )
                
                if min_buffer_size != AudioRecord.ERROR_BAD_VALUE:
                    self.buffer_size = max(self.buffer_size, min_buffer_size)
                    self.audio_record = AudioRecord(
                        source,
                        self.sample_rate,
                        channel_config,
                        audio_format,
                        self.buffer_size * 2
                    )
                    
                    if self.audio_record.getState() == AudioRecord.STATE_INITIALIZED:
                        Logger.info(f"DSP: Audio source {source} initialized successfully")
                        break
                    else:
                        self.audio_record.release()
                        self.audio_record = None
            except Exception as e:
                Logger.warning(f"DSP: Failed to initialize audio source {source}: {e}")
                continue
        
        if not self.audio_record:
            Logger.error("DSP: Failed to initialize any audio source")
            
    except Exception as e:
        Logger.error(f"DSP: Audio setup failed: {e}")

def start_recording(self):
    """Start recording from external mic"""
    if platform == 'android' and self.audio_record:
        try:
            self.audio_record.startRecording()
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._recording_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            Logger.info("DSP: Recording started")
            return True
        except Exception as e:
            Logger.error(f"DSP: Recording start failed: {e}")
            return False
    else:
        # Simulate for non-Android platforms
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._simulate_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        return True

def stop_recording(self):
    """Stop recording"""
    self.is_recording = False
    if platform == 'android' and self.audio_record:
        try:
            self.audio_record.stop()
            Logger.info("DSP: Recording stopped")
        except Exception as e:
            Logger.error(f"DSP: Recording stop failed: {e}")

def _recording_loop(self):
    """Main recording loop for Android"""
    buffer = np.zeros(self.buffer_size, dtype=np.int16)
    
    while self.is_recording:
        try:
            # Read audio data
            bytes_read = self.audio_record.read(buffer.tobytes(), 0, self.buffer_size * 2)
            
            if bytes_read > 0:
                # Convert to numpy array
                audio_data = np.frombuffer(buffer.tobytes()[:bytes_read], dtype=np.int16)
                audio_data = audio_data.astype(np.float32) / 32768.0  # Normalize
                
                # Add to circular buffer
                self.audio_data.extend(audio_data)
                
                # Calculate levels
                self.rms_level = np.sqrt(np.mean(audio_data**2))
                self.peak_level = np.max(np.abs(audio_data))
                
                # Calculate FFT for frequency analysis
                if len(audio_data) >= 512:
                    windowed = audio_data[:512] * np.hanning(512)
                    fft = np.abs(np.fft.fft(windowed))
                    self.fft_data = fft[:256]  # Take first half
            
            time.sleep(0.01)  # Small delay to prevent CPU overload
            
        except Exception as e:
            Logger.error(f"DSP: Recording loop error: {e}")
            break

def _simulate_audio(self):
    """Simulate audio data for testing on non-Android"""
    while self.is_recording:
        # Generate test signal
        t = np.linspace(0, self.buffer_size/self.sample_rate, self.buffer_size)
        test_signal = 0.1 * (np.sin(2*np.pi*440*t) + 0.5*np.sin(2*np.pi*880*t))
        
        self.audio_data.extend(test_signal)
        self.rms_level = np.sqrt(np.mean(test_signal**2))
        self.peak_level = np.max(np.abs(test_signal))
        
        # Generate test FFT
        windowed = test_signal[:512] * np.hanning(512)
        fft = np.abs(np.fft.fft(windowed))
        self.fft_data = fft[:256]
        
        time.sleep(0.05)

def get_frequency_bands(self):
    """Get frequency band levels for display"""
    if len(self.fft_data) == 0:
        return np.zeros(31)
    
    # 31-band frequency analysis
    freqs = np.fft.fftfreq(512, 1/self.sample_rate)[:256]
    
    # Standard 31-band frequencies
    band_freqs = [20, 25, 31, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 
                 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 
                 10000, 12500, 16000, 20000]
    
    band_levels = np.zeros(31)
    
    for i, freq in enumerate(band_freqs[:-1]):
        # Find frequency indices
        start_idx = np.argmin(np.abs(freqs - freq))
        end_idx = np.argmin(np.abs(freqs - band_freqs[i+1]))
        
        if start_idx < end_idx:
            band_levels[i] = np.mean(self.fft_data[start_idx:end_idx])
    
    # Convert to dB
    band_levels = 20 * np.log10(band_levels + 1e-10)
    band_levels = np.clip(band_levels + 60, 0, 60)  # Normalize to 0-60 dB range
    
    return band_levels
```

class DSPControlWidget(BoxLayout):
“”“Main DSP control interface”””

```
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.orientation = 'vertical'
    self.padding = 10
    self.spacing = 10
    
    self.audio_processor = AudioProcessor()
    self.is_analyzing = False
    
    self.build_interface()
    
    # Start update timer
    Clock.schedule_interval(self.update_display, 1/30)  # 30 FPS updates

def build_interface(self):
    """Build the main interface"""
    
    # Header
    header = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
    
    title = Label(text='Car Audio DSP Pro', font_size='20sp', 
                 size_hint_x=0.7, text_size=(None, None))
    
    self.status_label = Label(text='Ready', font_size='14sp',
                             size_hint_x=0.3, text_size=(None, None))
    
    header.add_widget(title)
    header.add_widget(self.status_label)
    self.add_widget(header)
    
    # Control buttons
    controls = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp')
    
    self.record_button = Button(text='Start Analysis', size_hint_x=0.5)
    self.record_button.bind(on_press=self.toggle_recording)
    
    self.save_button = Button(text='Save Config', size_hint_x=0.25)
    self.save_button.bind(on_press=self.save_config)
    
    self.load_button = Button(text='Load Config', size_hint_x=0.25)
    self.load_button.bind(on_press=self.load_config)
    
    controls.add_widget(self.record_button)
    controls.add_widget(self.save_button)
    controls.add_widget(self.load_button)
    self.add_widget(controls)
    
    # Level meters
    levels = BoxLayout(orientation='horizontal', size_hint_y=None, height='80dp')
    
    # RMS Level
    rms_box = BoxLayout(orientation='vertical')
    rms_box.add_widget(Label(text='RMS Level', size_hint_y=None, height='20dp'))
    self.rms_bar = ProgressBar(max=1.0, value=0)
    self.rms_label = Label(text='0.0 dB', size_hint_y=None, height='20dp')
    rms_box.add_widget(self.rms_bar)
    rms_box.add_widget(self.rms_label)
    
    # Peak Level
    peak_box = BoxLayout(orientation='vertical')
    peak_box.add_widget(Label(text='Peak Level', size_hint_y=None, height='20dp'))
    self.peak_bar = ProgressBar(max=1.0, value=0)
    self.peak_label = Label(text='0.0 dB', size_hint_y=None, height='20dp')
    peak_box.add_widget(self.peak_bar)
    peak_box.add_widget(self.peak_label)
    
    levels.add_widget(rms_box)
    levels.add_widget(peak_box)
    self.add_widget(levels)
    
    # Tabbed interface
    self.tab_panel = TabbedPanel(do_default_tab=False)
    
    # Real-time analyzer tab
    analyzer_tab = TabbedPanelItem(text='Real-Time Analyzer')
    analyzer_content = self.build_analyzer_tab()
    analyzer_tab.add_widget(analyzer_content)
    self.tab_panel.add_widget(analyzer_tab)
    
    # EQ tab
    eq_tab = TabbedPanelItem(text='31-Band EQ')
    eq_content = self.build_eq_tab()
    eq_tab.add_widget(eq_content)
    self.tab_panel.add_widget(eq_tab)
    
    # Channel control tab
    channel_tab = TabbedPanelItem(text='Channel Control')
    channel_content = self.build_channel_tab()
    channel_tab.add_widget(channel_content)
    self.tab_panel.add_widget(channel_tab)
    
    self.add_widget(self.tab_panel)

def build_analyzer_tab(self):
    """Build real-time frequency analyzer"""
    layout = BoxLayout(orientation='vertical', padding=10)
    
    # Frequency display (simplified bars)
    freq_layout = GridLayout(cols=31, size_hint_y=None, height='200dp')
    
    self.freq_bars = []
    band_labels = ['20', '25', '31', '40', '50', '63', '80', '100', '125', '160', 
                  '200', '250', '315', '400', '500', '630', '800', '1k', '1.25k', 
                  '1.6k', '2k', '2.5k', '3.15k', '4k', '5k', '6.3k', '8k', '10k', 
                  '12.5k', '16k', '20k']
    
    for i, label in enumerate(band_labels):
        bar_layout = BoxLayout(orientation='vertical')
        
        # Frequency bar (using ProgressBar rotated)
        bar = ProgressBar(max=60, value=0, size_hint_y=0.8)
        self.freq_bars.append(bar)
        
        # Label
        freq_label = Label(text=label, font_size='8sp', size_hint_y=0.2)
        
        bar_layout.add_widget(bar)
        bar_layout.add_widget(freq_label)
        freq_layout.add_widget(bar_layout)
    
    layout.add_widget(freq_layout)
    
    # Analysis controls
    controls = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
    
    # Gain adjustment
    controls.add_widget(Label(text='Display Gain:', size_hint_x=0.3))
    self.display_gain_slider = Slider(min=-20, max=20, value=0, step=1, size_hint_x=0.7)
    controls.add_widget(self.display_gain_slider)
    
    layout.add_widget(controls)
    
    return layout

def build_eq_tab(self):
    """Build 31-band EQ interface"""
    layout = BoxLayout(orientation='vertical', padding=10)
    
    # EQ sliders
    eq_layout = GridLayout(cols=31, size_hint_y=None, height='300dp')
    
    self.eq_sliders = []
    band_freqs = [20, 25, 31, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 
                 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 
                 10000, 12500, 16000, 20000]
    
    for freq in band_freqs:
        slider_layout = BoxLayout(orientation='vertical')
        
        # EQ slider
        eq_slider = Slider(min=-12, max=12, value=0, step=0.5, 
                          orientation='vertical', size_hint_y=0.8)
        self.eq_sliders.append(eq_slider)
        
        # Frequency label
        if freq >= 1000:
            label_text = f'{freq//1000}k'
        else:
            label_text = str(freq)
        
        freq_label = Label(text=label_text, font_size='8sp', size_hint_y=0.1)
        value_label = Label(text='0.0', font_size='8sp', size_hint_y=0.1)
        
        # Bind slider to update value label
        eq_slider.bind(value=lambda instance, value, label=value_label: 
                      setattr(label, 'text', f'{value:.1f}'))
        
        slider_layout.add_widget(eq_slider)
        slider_layout.add_widget(freq_label)
        slider_layout.add_widget(value_label)
        eq_layout.add_widget(slider_layout)
    
    layout.add_widget(eq_layout)
    
    # EQ controls
    controls = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
    
    reset_button = Button(text='Reset EQ', size_hint_x=0.33)
    reset_button.bind(on_press=self.reset_eq)
    
    flat_button = Button(text='Flat Response', size_hint_x=0.33)
    flat_button.bind(on_press=self.flat_eq)
    
    preset_button = Button(text='V-Shape', size_hint_x=0.33)
    preset_button.bind(on_press=self.v_shape_eq)
    
    controls.add_widget(reset_button)
    controls.add_widget(flat_button)
    controls.add_widget(preset_button)
    
    layout.add_widget(controls)
    
    return layout

def build_channel_tab(self):
    """Build channel control interface"""
    layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
    
    channels = ['Front Left', 'Front Right', 'Rear Left', 'Rear Right', 'Subwoofer', 'Center']
    self.channel_controls = {}
    
    for channel in channels:
        channel_box = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp')
        
        # Channel label
        channel_label = Label(text=channel, size_hint_y=None, height='25dp', font_size='14sp')
        channel_box.add_widget(channel_label)
        
        # Controls grid
        controls_grid = GridLayout(cols=4, size_hint_y=None, height='95dp')
        
        # Gain
        controls_grid.add_widget(Label(text='Gain'))
        gain_slider = Slider(min=-20, max=20, value=0, step=0.5)
        controls_grid.add_widget(gain_slider)
        
        # Volume
        controls_grid.add_widget(Label(text='Volume'))
        volume_slider = Slider(min=0, max=100, value=50, step=1)
        controls_grid.add_widget(volume_slider)
        
        # High Pass
        controls_grid.add_widget(Label(text='HPF'))
        hp_slider = Slider(min=20, max=500, value=80, step=5)
        controls_grid.add_widget(hp_slider)
        
        # Low Pass
        controls_grid.add_widget(Label(text='LPF'))
        lp_slider = Slider(min=1000, max=20000, value=20000, step=100)
        controls_grid.add_widget(lp_slider)
        
        # Delay
        controls_grid.add_widget(Label(text='Delay'))
        delay_slider = Slider(min=0, max=20, value=0, step=0.1)
        controls_grid.add_widget(delay_slider)
        
        # Phase
        controls_grid.add_widget(Label(text='Phase'))
        phase_switch = Switch(active=False)
        controls_grid.add_widget(phase_switch)
        
        # Mute
        controls_grid.add_widget(Label(text='Mute'))
        mute_switch = Switch(active=False)
        controls_grid.add_widget(mute_switch)
        
        # Bypass
        controls_grid.add_widget(Label(text='Bypass'))
        bypass_switch = Switch(active=False)
        controls_grid.add_widget(bypass_switch)
        
        channel_box.add_widget(controls_grid)
        layout.add_widget(channel_box)
        
        # Store references
        self.channel_controls[channel] = {
            'gain': gain_slider,
            'volume': volume_slider,
            'highpass': hp_slider,
            'lowpass': lp_slider,
            'delay': delay_slider,
            'phase': phase_switch,
            'mute': mute_switch,
            'bypass': bypass_switch
        }
    
    return layout

def toggle_recording(self, instance):
    """Toggle audio recording/analysis"""
    if not self.is_analyzing:
        if self.audio_processor.start_recording():
            self.is_analyzing = True
            self.record_button.text = 'Stop Analysis'
            self.status_label.text = 'Analyzing...'
        else:
            self.status_label.text = 'Mic Error'
    else:
        self.audio_processor.stop_recording()
        self.is_analyzing = False
        self.record_button.text = 'Start Analysis'
        self.status_label.text = 'Ready'

def update_display(self, dt):
    """Update real-time displays"""
    if not self.is_analyzing:
        return
    
    # Update level meters
    rms_db = 20 * np.log10(max(self.audio_processor.rms_level, 1e-10)) + 60
    peak_db = 20 * np.log10(max(self.audio_processor.peak_level, 1e-10)) + 60
    
    self.rms_bar.value = max(0, min(1, rms_db / 60))
    self.peak_bar.value = max(0, min(1, peak_db / 60))
    
    self.rms_label.text = f'{rms_db - 60:.1f} dB'
    self.peak_label.text = f'{peak_db - 60:.1f} dB'
    
    # Update frequency analyzer
    if hasattr(self, 'freq_bars'):
        band_levels = self.audio_processor.get_frequency_bands()
        gain_offset = self.display_gain_slider.value if hasattr(self, 'display_gain_slider') else 0
        
        for i, bar in enumerate(self.freq_bars):
            if i < len(band_levels):
                adjusted_level = band_levels[i] + gain_offset
                bar.value = max(0, min(60, adjusted_level))

def reset_eq(self, instance):
    """Reset EQ to flat"""
    for slider in self.eq_sliders:
        slider.value = 0

def flat_eq(self, instance):
    """Set flat EQ response"""
    self.reset_eq(instance)

def v_shape_eq(self, instance):
    """Set V-shape EQ curve"""
    # Bass boost and treble boost
    v_curve = [-2, -1, 0, 2, 4, 6, 4, 2, 0, -1, -2, -3, -4, -4, -4, 
              -4, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 4, 2, 0, -2]
    
    for i, slider in enumerate(self.eq_sliders):
        if i < len(v_curve):
            slider.value = v_curve[i]

def save_config(self, instance):
    """Save current configuration"""
    config = {
        'eq': [slider.value for slider in self.eq_sliders],
        'channels': {}
    }
    
    for channel, controls in self.channel_controls.items():
        config['channels'][channel] = {
            'gain': controls['gain'].value,
            'volume': controls['volume'].value,
            'highpass': controls['highpass'].value,
            'lowpass': controls['lowpass'].value,
            'delay': controls['delay'].value,
            'phase': controls['phase'].active,
            'mute': controls['mute'].active,
            'bypass': controls['bypass'].active
        }
    
    try:
        if platform == 'android':
            from android.storage import primary_external_storage_path
            config_path = primary_external_storage_path() + '/DSP_Config.json'
        else:
            config_path = 'DSP_Config.json'
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.status_label.text = 'Config Saved'
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Ready'), 2)
        
    except Exception as e:
        Logger.error(f"DSP: Save config failed: {e}")
        self.status_label.text = 'Save Failed'

def load_config(self, instance):
    """Load configuration"""
    try:
        if platform == 'android':
            from android.storage import primary_external_storage_path
            config_path = primary_external_storage_path() + '/DSP_Config.json'
        else:
            config_path = 'DSP_Config.json'
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Load EQ
        if 'eq' in config:
            for i, value in enumerate(config['eq']):
                if i < len(self.eq_sliders):
                    self.eq_sliders[i].value = value
        
        # Load channels
        if 'channels' in config:
            for channel, settings in config['channels'].items():
                if channel in self.channel_controls:
                    controls = self.channel_controls[channel]
                    for param, value in settings.items():
                        if param in controls:
                            if isinstance(controls[param], Slider):
                                controls[param].value = value
                            elif isinstance(controls[param], Switch):
                                controls[param].active = value
        
        self.status_label.text = 'Config Loaded'
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Ready'), 2)
        
    except Exception as e:
        Logger.error(f"DSP: Load config failed: {e}")
        self.status_label.text = 'Load Failed'
```

class DSPApp(App):
“”“Main DSP Application”””

```
def build(self):
    self.title = 'Car Audio DSP Pro'
    return DSPControlWidget()

def on_pause(self):
    """Handle app pause"""
    return True

def on_resume(self):
    """Handle app resume"""
    pass
```

if **name** == ‘**main**’:
DSPApp().run()