import time
import openai
from selenium import webdriver
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
    print("Initializing Chrome WebDriver")
    
    options = webdriver.ChromeOptions()
    options.binary_location = os.getenv("GOOGLE_CHROME_BIN")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(os.getenv("CHROMEDRIVER_PATH"), options=options)

    try:
        print("Navigating to YouTube URL:", youtube_url)
        driver.get(youtube_url)
        time.sleep(5)  # Allow time for the page to load completely
        print("Page loaded. Page source length:", len(driver.page_source))

        # Click the 'More' button to expand the description
        try:
            print("Attempting to click 'More' button...")
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//tp-yt-paper-button[@id="expand"]'))
            )
            more_button.click()
            print("'More' button clicked successfully.")
            time.sleep(2)  # Wait for the description to expand
        except Exception as e:
            print("Error clicking 'More' button:", e)
            return None

        # Click the 'Show transcript' button
        try:
            print("Attempting to click 'Show transcript' button...")
            transcript_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Show transcript")]'))
            )
            transcript_button.click()
            time.sleep(5)  # Wait for the transcript to load
            print("'Show transcript' button clicked successfully.")
        except Exception as e:
            print("Error clicking 'Show transcript' button:", e)
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
        print("Driver session ended.")

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
