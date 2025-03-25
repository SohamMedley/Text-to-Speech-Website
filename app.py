from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import requests
import json
import uuid
import time
import logging

app = Flask(__name__)
app.debug = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment variable or use a default for testing
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

# ElevenLabs API endpoints
ELEVENLABS_VOICES_URL = "https://api.elevenlabs.io/v1/voices"
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/"

# Create a directory for storing audio files if it doesn't exist
os.makedirs('static/audio', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

@app.route('/features')
def features():
    return render_template('features.html', active_page='features')

@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    return render_template('search_results.html', query=query)

@app.route('/get_voices')
def get_voices():
    try:
        # Always return mock data to avoid API restrictions
        mock_voices = [
            {"voice_id": "mock_voice_1", "name": "Demo Voice 1 (Male)"},
            {"voice_id": "mock_voice_2", "name": "Demo Voice 2 (Female)"},
            {"voice_id": "mock_voice_3", "name": "Demo Voice 3 (Neutral)"},
            {"voice_id": "mock_voice_4", "name": "Demo Voice 4 (Child)"},
            {"voice_id": "mock_voice_5", "name": "Demo Voice 5 (Elder)"}
        ]
        return jsonify({"voices": mock_voices})
        
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    try:
        # Get request data
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        text = data.get('text')
        voice_id = data.get('voice_id')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if not voice_id:
            return jsonify({"error": "No voice ID provided"}), 400
        
        # Use local fallback instead of ElevenLabs API
        # We'll use pre-recorded demo files based on the voice_id
        
        # Map voice_id to demo files
        voice_to_file = {
            "mock_voice_1": "demo_male.mp3",
            "mock_voice_2": "demo_female.mp3",
            "mock_voice_3": "demo_neutral.mp3",
            "mock_voice_4": "demo_child.mp3",
            "mock_voice_5": "demo_elder.mp3"
        }
        
        # Get the appropriate demo file or use a default
        demo_file = voice_to_file.get(voice_id, "demo_neutral.mp3")
        
        # Return the URL to the demo file
        file_url = f"/static/audio/{demo_file}"
        
        logger.info(f"Using demo file: {file_url}")
        return jsonify({"success": True, "file_url": file_url, "demo_mode": True})
        
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    # Check if the file exists in the static/audio directory
    if os.path.exists(os.path.join('static/audio', filename)):
        return send_from_directory('static/audio', filename)
    
    # If the file doesn't exist, serve a default audio file
    return send_from_directory('static/audio', 'fallback.mp3')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Create demo audio files if they don't exist
    demo_files = [
        "demo_male.mp3", 
        "demo_female.mp3", 
        "demo_neutral.mp3", 
        "demo_child.mp3", 
        "demo_elder.mp3",
        "fallback.mp3"
    ]
    
    for demo_file in demo_files:
        file_path = os.path.join('static/audio', demo_file)
        if not os.path.exists(file_path):
            # Create an empty file as a placeholder
            with open(file_path, 'wb') as f:
                f.write(b'')
            logger.info(f"Created placeholder file: {file_path}")
    
    app.run(host='0.0.0.0', port=port)

