import queue
import wave
import pathlib
import subprocess
import signal
import sounddevice as sd
import webrtcvad
import pyttsx3
from gtts import gTTS
import requests.sessions as rs

class AudioHandler:
    def __init__(self, sample_rate=16000, frame_ms=20, channels=1, vad_mode=2):
        self.SAMPLE_RATE = sample_rate
        self.FRAME_MS = frame_ms
        self.CHANNELS = channels
        self.FRAME_LEN = self.SAMPLE_RATE * self.FRAME_MS // 1000
        
        self.vad = webrtcvad.Vad(vad_mode)
        self.audio_q = queue.Queue()
        self.engine = pyttsx3.init()
        
        # Create output directory
        self.OUT_DIR = pathlib.Path("audio")
        self.OUT_DIR.mkdir(exist_ok=True)
        
        # TTS settings
        self.TTS_LANG = "en"
        self.GTTS_TIMEOUT_SEC = 5

    def _audio_callback(self, indata, *_):
        """Callback for audio input stream"""
        self.audio_q.put(indata.copy().tobytes())

    def write_wav(self, path: pathlib.Path, pcm: bytes):
        """Write PCM data to WAV file"""
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(pcm)

    def say_offline(self, text: str):
        """Use offline TTS engine"""
        self.engine.say(text)
        self.engine.runAndWait()

    def try_gtts(self, text: str, mp3_path: pathlib.Path) -> bool:
        """Try to use Google TTS with timeout"""
        try:
            orig = rs.Session.request
            def limited(self, *a, **kw):
                kw.setdefault("timeout", self.GTTS_TIMEOUT_SEC)
                return orig(self, *a, **kw)
            rs.Session.request = limited
            gTTS(text, lang=self.TTS_LANG).save(str(mp3_path))
            return True
        except Exception as e:
            print(f"⚠  gTTS failed ({e.__class__.__name__}: {e}). Falling back to offline TTS.")
            mp3_path.unlink(missing_ok=True)
            return False
        finally:
            rs.Session.request = orig

    def speak(self, text: str, mp3_path: pathlib.Path):
        """Speak text using either online or offline TTS"""
        if self.try_gtts(text, mp3_path):
            proc = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(mp3_path)],
                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
            try:
                proc.wait()
            except KeyboardInterrupt:
                proc.send_signal(signal.SIGINT)
                proc.wait()
                raise
        else:
            self.say_offline(text)

    def record_until_silence(self, timeout_sec: float) -> bytes:
        """Record audio until silence is detected"""
        buf, silent_frames, spoke = [], 0, False
        with sd.InputStream(
            channels=self.CHANNELS,
            samplerate=self.SAMPLE_RATE,
            blocksize=self.FRAME_LEN,
            dtype="int16",
            callback=self._audio_callback
        ):
            while True:
                frame = self.audio_q.get()
                buf.append(frame)
                if self.vad.is_speech(frame, self.SAMPLE_RATE):
                    spoke, silent_frames = True, 0
                else:
                    silent_frames += 1
                if spoke and silent_frames * self.FRAME_MS / 1000 >= timeout_sec:
                    break
        return b"".join(buf) if spoke else b"" 