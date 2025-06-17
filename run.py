#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
import os
from pathlib import Path
import sys
from io import StringIO
import logging
import shutil

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, "app")
sys.path.insert(0, app_dir)

from app.voice_assistant import VoiceAssistant
import threading
import queue

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    static_folder='web/static',
    template_folder='web'
)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Clear audio directory on startup
AUDIO_DIR = Path("audio")
if AUDIO_DIR.exists():
    shutil.rmtree(AUDIO_DIR)
AUDIO_DIR.mkdir(exist_ok=True)
logger.info("Cleared audio directory")

# Initialize the voice assistant and message queue
assistant = VoiceAssistant()
message_queue = queue.Queue()

class WebOutput:
    def __init__(self, message_queue):
        self.message_queue = message_queue
        self.buffer = StringIO()
        self.is_new_conversation = True

    def write(self, text):
        self.buffer.write(text)
        text = self.buffer.getvalue()
        
        # Check for user speech
        if "You said" in text:
            message = text.split("You said")[1].strip()
            logger.info(f"Detected user speech: {message}")
            self.message_queue.put({
                'type': 'user_speech',
                'text': message
            })
            self.buffer = StringIO()
        
        # Check for assistant reply
        elif "GPT-4o reply" in text:
            message = text.split("GPT-4o reply")[1].strip()
            logger.info(f"Detected assistant reply: {message}")
            self.message_queue.put({
                'type': 'assistant_reply',
                'text': message
            })
            self.buffer = StringIO()
        
        # Check for user's answer to continue
        elif "Would you like to start another conversation?" in text:
            logger.info("Detected continue prompt")
            self.message_queue.put({
                'type': 'continue_prompt',
                'text': "Would you like to start another conversation? (yes/no):"
            })
            self.buffer = StringIO()
        
        # Check for user's answer
        elif "Your answer" in text:
            answer = text.split("Your answer")[1].strip().lower()
            logger.info(f"Detected user answer: {answer}")
            if 'yes' in answer:
                self.message_queue.put({
                    'type': 'user_answer',
                    'text': "Yes, let's continue!",
                    'action': 'continue'
                })
                self.is_new_conversation = True
            elif 'no' in answer:
                self.message_queue.put({
                    'type': 'user_answer',
                    'text': "No, let's end here.",
                    'action': 'end'
                })
                self.message_queue.put({
                    'type': 'assistant_reply',
                    'text': "Goodbye! Have a good day!"
                })
            self.buffer = StringIO()
        
        # Check for status updates
        elif "Speak now" in text:
            logger.info("Detected listening status")
            self.message_queue.put({
                'type': 'status',
                'text': 'Listening...',
                'state': 'recording'
            })
            self.buffer = StringIO()
        elif "Processing" in text:
            logger.info("Detected processing status")
            self.message_queue.put({
                'type': 'status',
                'text': 'Processing...',
                'state': 'processing'
            })
            self.buffer = StringIO()
        elif "Ready to start" in text:
            logger.info("Detected ready status")
            if self.is_new_conversation:
                self.message_queue.put({
                    'type': 'assistant_reply',
                    'text': "What would you like to talk about?"
                })
                self.is_new_conversation = False
            self.message_queue.put({
                'type': 'status',
                'text': 'Ready to start',
                'state': 'ready'
            })
            self.buffer = StringIO()

    def flush(self):
        pass

def run_voice_assistant():
    """Run the voice assistant in a separate thread"""
    try:
        # Redirect stdout to our custom output handler
        original_stdout = sys.stdout
        sys.stdout = WebOutput(message_queue)
        
        # Run the assistant
        assistant.run()
        
        # Restore stdout
        sys.stdout = original_stdout
    except Exception as e:
        message_queue.put({"type": "error", "message": str(e)})

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('web/static', path)

@app.route('/api/start', methods=['POST'])
def start_assistant():
    """Start the voice assistant"""
    try:
        # Start the voice assistant in a separate thread
        thread = threading.Thread(target=run_voice_assistant)
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current status of the voice assistant"""
    try:
        messages = []
        # Get all available messages from the queue
        while not message_queue.empty():
            message = message_queue.get()
            logger.info(f"Sending message to client: {message}")
            messages.append(message)
        
        if messages:
            return jsonify({"messages": messages})
        return jsonify({"status": "running"})
    except Exception as e:
        logger.error(f"Error in get_status: {str(e)}")
        return jsonify({"error": str(e)}), 500

def main():
    try:
        # Get port from environment variable for Render deployment
        port = int(os.environ.get("PORT", 9000))
        
        # Start the Flask server
        logger.info("🚀 Starting Voice Assistant Web Server...")
        logger.info(f"🌐 Open http://localhost:{port} in your browser")
        app.run(host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
    finally:
        logger.info("🚪 Session closed.")

if __name__ == "__main__":
    main() 