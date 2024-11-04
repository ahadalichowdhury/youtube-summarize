import time
import openai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from flask import Flask, request, jsonify
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask_cors import CORS  # Import CORS
from dotenv import load_dotenv
import os  # Import os to access environment variables

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
CORS(app)

def get_youtube_transcript(youtube_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Specify the path to the ChromeDriver executable
    service = Service(executable_path='/app/.chromedriver/bin/chromedriver')

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(youtube_url)

    # Add your code to extract the transcript from the page here
    transcript = "Dummy transcript from YouTube video."
    
    driver.quit()
    return transcript

def summarize_transcript(transcript):
    # Join the transcript lines into a single string
    transcript_text = "\n".join(transcript)

    # Call the OpenAI API to summarize the transcript
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # Use the appropriate model
        messages=[
            {
                "role": "user", 
                "content": (
                    f"Make sure to explain the key points clearly and include relevant details."
                    f"In the transcript, the speaker can talk about anything. If the speaker talks about any code or command, provide it in a completed version with proper explanation. "
                    f"Respond in clean, proper HTML so the application can render it straight away. Normal text will be wrapped in a <p> tag. Links will be formatted as HTML links with an <a> tag. "
                    f"Links will have yellow font. Use divs and headings to properly separate different sections. Ensure text doesn't overlap and there is adequate line spacing. "
                    f"Only output pure HTML. No markdown. All answers, titles, lists, headers, paragraphs - reply in fully styled HTML as the app will render and parse your responses as you reply. "
                    f"Only if asked about programming problems requiring code, use a dark background and white font for that code. "
                    f"Here’s the transcript: \n\n{transcript_text}\n\n,"
                )
            }
        ]
    )

    # Extract and return the summary from the response
    summary = response['choices'][0]['message']['content']
    return summary

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the YouTube Summarizer API"}), 200

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({"error": "You must provide a YouTube video URL."}), 400

    print("Received YouTube URL for summarization:", youtube_url)
    transcript = get_youtube_transcript(youtube_url)

    if transcript:
        summary = summarize_transcript(transcript)
        return jsonify({"summary": summary}), 200
    else:
        return jsonify({"error": "No transcript found for the provided URL."}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
