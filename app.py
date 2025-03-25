from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import uuid
import time

app = Flask(__name__)
app.debug = True

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
        # If no API key is provided, return mock data for demo purposes
        if not ELEVENLABS_API_KEY:
            # Mock data for demonstration
            mock_voices = [
                {"voice_id": "mock_voice_1", "name": "Demo Voice 1 (Male)"},
                {"voice_id": "mock_voice_2", "name": "Demo Voice 2 (Female)"},
                {"voice_id": "mock_voice_3", "name": "Demo Voice 3 (Neutral)"},
                {"voice_id": "mock_voice_4", "name": "Demo Voice 4 (Child)"},
                {"voice_id": "mock_voice_5", "name": "Demo Voice 5 (Elder)"}
            ]
            return jsonify({"voices": mock_voices})
        
        # Make request to ElevenLabs API
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        response = requests.get(ELEVENLABS_VOICES_URL, headers=headers)
        data = response.json()
        
        # Extract relevant voice information
        voices = []
        for voice in data.get("voices", []):
            voices.append({
                "voice_id": voice.get("voice_id"),
                "name": voice.get("name")
            })
        
        return jsonify({"voices": voices})
    
    except Exception as e:
        app.logger.error(f"Error fetching voices: {str(e)}")
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
        stability = data.get('stability', 0.5)
        clarity = data.get('clarity', 0.5)
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        if not voice_id:
            return jsonify({"error": "No voice ID provided"}), 400
        
        # If no API key is provided, return mock data for demo purposes
        if not ELEVENLABS_API_KEY:
            # For demo, we'll just create a filename and pretend we generated audio
            filename = f"demo_speech_{uuid.uuid4()}.mp3"
            file_path = os.path.join('static/audio', filename)
            
            # Create an empty file to simulate the process
            with open(file_path, 'w') as f:
                f.write("This is a demo file. In a real deployment, this would be audio content.")
            
            # Return the URL to the file
            file_url = f"/static/audio/{filename}"
            return jsonify({"success": True, "file_url": file_url})
        
        # Make request to ElevenLabs API
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": clarity
            }
        }
        
        response = requests.post(
            f"{ELEVENLABS_TTS_URL}{voice_id}",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"API Error: {response.text}"}), response.status_code
        
        # Save the audio file
        filename = f"speech_{uuid.uuid4()}.mp3"
        file_path = os.path.join('static/audio', filename)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        # Return the URL to the file
        file_url = f"/static/audio/{filename}"
        return jsonify({"success": True, "file_url": file_url})
    
    except Exception as e:
        app.logger.error(f"Error generating speech: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

