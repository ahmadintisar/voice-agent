import datetime
import re
from pathlib import Path

from app.audio.audio_handler import AudioHandler
from app.ai.ai_handler import AIHandler
from app.utils.config import Config

class VoiceAssistant:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.audio_handler = AudioHandler(
            sample_rate=self.config.SAMPLE_RATE,
            frame_ms=self.config.FRAME_MS,
            channels=self.config.CHANNELS,
            vad_mode=self.config.VAD_MODE
        )
        self.ai_handler = AIHandler(
            whisper_model=self.config.WHISPER_MODEL,
            gpt_model=self.config.GPT_MODEL
        )
        self.round_no = 1

    def process_user_input(self, pcm: bytes) -> tuple[str, Path]:
        """Process user's audio input and return transcript and file path"""
        if not pcm:
            return "", None

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        wav_path = self.config.OUT_DIR / f"speech_{ts}.wav"
        self.audio_handler.write_wav(wav_path, pcm)

        transcript = self.ai_handler.transcribe_audio(wav_path)
        wav_path.with_suffix(".txt").write_text(transcript + "\n")
        return transcript, wav_path

    def handle_continuation(self) -> bool:
        """Handle the continuation prompt and user response"""
        cont_prompt = "Would you like to continue the chat? Please say Yes or No."
        print(cont_prompt)
        
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.audio_handler.speak(cont_prompt, self.config.OUT_DIR / f"prompt_{ts}.mp3")

        print("🗣  Speak now…")
        ans_pcm = self.audio_handler.record_until_silence(self.config.ANS_SILENCE_SEC)
        
        if not ans_pcm:
            return False

        tmp = self.config.OUT_DIR / "ans_temp.wav"
        self.audio_handler.write_wav(tmp, ans_pcm)
        ans_text = self.ai_handler.transcribe_audio(tmp).lower().strip()
        tmp.unlink(missing_ok=True)
        
        print(f"📜 Detected answer: {ans_text!r}")

        if re.match(r"^\s*y(es)?\b", ans_text):
            return True
        elif re.match(r"^\s*n(o)?\b", ans_text):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.audio_handler.speak("Good-bye!", self.config.OUT_DIR / f"goodbye_{ts}.mp3")
            return False
        return False

    def run(self):
        """Main conversation loop"""
        print("🤖  CypherGuard voice assistant ready.")

        while True:
            print(f"\n🎙  [Round {self.round_no}] Speak now… (auto-stop after {self.config.END_SILENCE_SEC}s silence)")
            pcm = self.audio_handler.record_until_silence(self.config.END_SILENCE_SEC)
            
            transcript, wav_path = self.process_user_input(pcm)
            if not transcript:
                print("No speech detected — exiting.")
                break

            print("\n—— You said ——\n" + transcript + "\n")

            try:
                reply = self.ai_handler.get_gpt_response(transcript)
                wav_path.with_suffix(".gpt.txt").write_text(reply + "\n")
                print("—— GPT-4o reply ——\n" + reply + "\n")
                
                mp3_path = wav_path.with_suffix(".mp3")
                self.audio_handler.speak(reply, mp3_path)

                if not self.handle_continuation():
                    break
                    
                self.round_no += 1

            except KeyboardInterrupt:
                print("⏹  Operation cancelled. Exiting.")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                break 