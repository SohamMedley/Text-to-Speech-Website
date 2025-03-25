from flask import Flask, request, jsonify, render_template, send_file
import requests
import os
import io
import time

app = Flask(__name__, static_folder='static', template_folder='templates')

# The API key should be stored as an environment variable in production
# For this example, I'll use a placeholder - replace with your actual key securely
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', 'your-default-key')

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
    # In a real application, you would implement actual search functionality
    return render_template('search_results.html', query=query)

@app.route('/get_voices', methods=['GET'])
def get_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch voices"}), 400

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')
    voice_id = data.get('voice_id', 'EXAVITQu4vr4xnSDxMaL')  # Default voice
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        # Generate a unique filename based on timestamp
        filename = f"speech_{int(time.time())}.mp3"
        file_path = os.path.join('static', 'audio', filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the audio file
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return jsonify({"success": True, "file_url": f"/static/audio/{filename}"})
    else:
        return jsonify({"error": "Failed to generate speech", "details": response.text}), 400

if __name__ == '__main__':
    # Create audio directory if it doesn't exist
    os.makedirs(os.path.join('static', 'audio'), exist_ok=True)
    app.run(host='0.0.0.0', port=port)

print("Flask Text-to-Speech application is ready to run!")
