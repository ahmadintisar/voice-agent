import os
from pathlib import Path
import openai
from faster_whisper import WhisperModel
from dotenv import load_dotenv

class AIHandler:
    def __init__(self, whisper_model="tiny.en", gpt_model="gpt-4"):
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.client = openai.OpenAI()
        self.gpt_model = gpt_model
        self.system_prompt = (
            "You are CypherGuard's technical voice assistant. "
            "Give concise, actionable answers with code snippets when helpful. Keep it very brief and to the point. Donot include any other text or comments and code in the response."
        )
        
        # Initialize Whisper
        self.whisper = WhisperModel(whisper_model, device="cpu", compute_type="int8")

    def transcribe_audio(self, audio_path: Path) -> str:
        """Transcribe audio file using Whisper"""
        try:
            segments, _ = self.whisper.transcribe(str(audio_path), vad_filter=False)
            return "".join(s.text for s in segments).strip()
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    def get_gpt_response(self, user_input: str) -> str:
        """Get response from GPT model"""
        try:
            response = self.client.chat.completions.create(
                model=self.gpt_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"GPT request failed: {str(e)}") 