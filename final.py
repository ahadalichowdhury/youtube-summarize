import time
import openai
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from flask_cors import CORS  # Import CORS
# Set your OpenAI API key
from dotenv import load_dotenv
import os  # Import os to access environment variables

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
CORS(app)
def get_youtube_transcript(youtube_url):
    # Set up the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (optional)
    #those for aws ec2 instance
    # options.binary_location = "/usr/bin/google-chrome"  # Adjust this if your path is different it only use for deployment
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    options.add_argument("--remote-debugging-port=9222")  # Optional: Debugging port
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    try:
        # Navigate to the YouTube video URL
        driver.get(youtube_url)
        
        # Allow time for the page to load completely
        time.sleep(5)

        # Click the 'More' button to expand the description
        try:
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//tp-yt-paper-button[@id="expand"]'))
            )
            more_button.click()
            time.sleep(2)  # Wait for the description to expand
        except Exception as e:
            print("Could not find or click the 'More' button:", e)
            return None

        # Click the 'Show transcript' button
        try:
            transcript_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Show transcript")]'))
            )
            transcript_button.click()
            time.sleep(5)  # Wait for the transcript to load
        except Exception as e:
            print("Could not find or click the 'Show transcript' button:", e)
            return None

        # Attempt to retrieve the transcript text
        try:
            transcript_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'yt-formatted-string.segment-text'))
            )
            transcript = [element.text for element in transcript_elements]
            if not transcript:
                print("No transcript found in the retrieved elements.")
                return None
            else:
                print("Transcript retrieved successfully.")
        except Exception as e:
            print("Could not retrieve transcript text:", e)
            return None

        return transcript

    finally:
        driver.quit()

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
                    f"In the transcript, the speaker can talk about anything. If you notice any code or command being mentioned, "
                    f"provide the complete version with a proper explanation. Respond in clean, proper HTML so the application "
                    f"can render it straight away. Normal text will be wrapped in a <p> tag. Format links as HTML links with an "
                    f"<a> tag. Links will have yellow font. Use divs and headings to separate different sections. Ensure text "
                    f"doesn't overlap and there is adequate line spacing. Output only pure HTML. No markdown. Here’s the transcript: \n\n{transcript_text}\n\n"
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

    transcript = get_youtube_transcript(youtube_url)

    if transcript:
        summary = summarize_transcript(transcript)
        return jsonify({"summary": summary}), 200
    else:
        return jsonify({"error": "No transcript found for the provided URL."}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # Set host to '0.0.0.0' for external access
