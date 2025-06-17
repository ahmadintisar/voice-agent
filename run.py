#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os
from pathlib import Path
import sys
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
app = Flask(__name__)
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

def run_voice_assistant():
    """Run the voice assistant in a separate thread"""
    try:
        assistant.run()
    except Exception as e:
        message_queue.put({"type": "error", "message": str(e)})

@app.route('/api/start', methods=['POST'])
def start_assistant():
    """Start the voice assistant"""
    try:
        # Start the voice assistant in a separate thread
        thread = threading.Thread(target=run_voice_assistant)
        thread.daemon = True
        thread.start()
        return jsonify({
            "status": "success",
            "message": "Voice assistant started successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current status of the voice assistant"""
    try:
        messages = []
        # Get all available messages from the queue
        while not message_queue.empty():
            message = message_queue.get()
            logger.info(f"Processing message: {message}")
            messages.append(message)
        
        if messages:
            return jsonify({
                "status": "success",
                "messages": messages
            })
        return jsonify({
            "status": "success",
            "message": "Voice assistant is running",
            "messages": []
        })
    except Exception as e:
        logger.error(f"Error in get_status: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/stop', methods=['POST'])
def stop_assistant():
    """Stop the voice assistant"""
    try:
        # TODO: Implement proper stop logic
        return jsonify({
            "status": "success",
            "message": "Voice assistant stopped successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def main():
    try:
        # Get port from environment variable or use default
        port = int(os.environ.get("PORT", 9000))
        
        # Start the Flask server
        logger.info("🚀 Starting Voice Assistant API Server...")
        logger.info(f"🌐 API Server running at http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
    finally:
        logger.info("🚪 Session closed.")

if __name__ == "__main__":
    main() 