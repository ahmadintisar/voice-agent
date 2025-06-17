from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    # Audio settings
    SAMPLE_RATE: int = 16000
    FRAME_MS: int = 20
    CHANNELS: int = 1
    VAD_MODE: int = 2
    
    # Silence detection
    END_SILENCE_SEC: float = 2.0
    ANS_SILENCE_SEC: float = 1.5
    
    # AI models
    WHISPER_MODEL: str = "tiny.en"
    GPT_MODEL: str = "gpt-4"
    
    # Output settings
    OUT_DIR: Path = Path("audio")
    TTS_LANG: str = "en"
    GTTS_TIMEOUT_SEC: int = 5 