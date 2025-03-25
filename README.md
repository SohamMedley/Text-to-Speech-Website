Voicify - Text to Speech Converter by Soham
Voicify is a web application that transforms text into natural-sounding speech using advanced AI powered by the ElevenLabs API. The project uses Flask for the backend along with HTML, CSS, and JavaScript for a responsive and user-friendly frontend.

Features
Text-to-Speech Conversion: Convert your text to natural speech in seconds.

Voice Customization: Choose from multiple voices and adjust settings like stability and clarity.

Audio Download: Download the generated speech as an MP3 file.

Responsive UI: Enjoy a seamless experience across devices.

Search & Navigation: Built-in pages including Home, Features, About, and Contact.

Prerequisites
Python 3.x

pip

Installation and Running Locally
Clone the repository:

bash
Copy
Edit
git clone https://github.com/SohamMedley/Text-to-Speech-Website.git
Navigate to the project folder:

vbnet
Copy
Edit
cd Text-to-Speech-Website
Install required packages:

nginx
Copy
Edit
pip install flask requests
Run the application:

nginx
Copy
Edit
python app.py
The app will be available at http://127.0.0.1:5000/.

Deployment on Render
To deploy Voicify on Render, use the following guidelines when filling out the web service configuration:

Name:
Set a unique name for your web service, for example:
Text-to-Speech-Website

Project:
Optionally add this web service to a project if you have one.

Language:
Change the language from "Node" to Python since this is a Flask application.

Branch:
Set the branch to deploy (e.g., main).

Region:
Choose a region that best fits your needs (e.g., Singapore for Southeast Asia or Oregon for US West).

Root Directory (Optional):
Leave blank if your project is in the repository root.

Build Command:
Python projects usually do not require a build step, so you can leave this empty unless you have custom build steps.

Start Command:
Set this to:

nginx
Copy
Edit
python app.py
Instance Type:
Choose based on your project needs (for hobby projects you can select the Free tier).
