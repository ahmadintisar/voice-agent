# CypherGuard Voice Assistant

A voice-enabled AI assistant that uses OpenAI's GPT-4 for natural conversations.

## Project Structure

```
voice_agent/
├── .env                    # Environment variables (API keys)
├── .gitignore             # Git ignore file
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── run.py                # Main application entry point
├── setup.py              # Package setup file
├── src/                  # Source code directory
│   ├── __init__.py
│   ├── voice_assistant.py    # Main voice assistant class
│   ├── ai/               # AI-related modules
│   │   ├── __init__.py
│   │   └── ai_handler.py     # GPT and Whisper integration
│   ├── audio/           # Audio processing modules
│   │   ├── __init__.py
│   │   └── audio_handler.py  # Audio recording and playback
│   └── utils/           # Utility modules
│       ├── __init__.py
│       └── config.py         # Configuration settings
└── web/                 # Web interface
    ├── index.html           # Main HTML file
    ├── static/             # Static assets
    │   ├── css/
    │   │   └── style.css    # Stylesheet
    │   └── js/
    │       └── app.js       # Frontend JavaScript
    └── templates/          # HTML templates
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd voice_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
python run.py
```

6. Open your browser and navigate to:
```
http://localhost:9000
```

## Features

- Voice input and output
- Natural language conversation with GPT-4
- Web interface for interaction
- Automatic speech recognition
- Text-to-speech responses
- Conversation history
- Easy-to-use controls

## Development

The project uses:
- Flask for the web server
- OpenAI's GPT-4 for AI responses
- Whisper for speech recognition
- gTTS for text-to-speech
- Web Audio API for browser-based audio handling

## Deployment

The application can be deployed to Render.com. Make sure to:
1. Set the `OPENAI_API_KEY` environment variable
2. Use Python 3.12.0
3. Set the port to 9000

## License

[Your License Here] 