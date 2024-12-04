# YouTube Summary API

A powerful API service that generates summaries of YouTube videos using OpenAI's language models. This project allows users to get concise summaries of YouTube video content by simply providing the video URL.

## Features

- Extract text content from YouTube videos
- Generate AI-powered summaries using OpenAI
- RESTful API endpoints for easy integration
- Docker support for containerized deployment
- Web interface for easy testing and demonstration

## Technologies Used

- Python 3.x
- Flask (Web Framework)
- OpenAI API
- Selenium (for YouTube content extraction)
- Docker
- HTML/CSS/JavaScript (Frontend)

## Prerequisites

Before running this project, make sure you have:

- Python 3.x installed
- OpenAI API key
- Docker (optional, for containerized deployment)
- Chrome WebDriver (automatically managed by webdriver-manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ahadalichowdhury/youtube-summarize.git
cd youtube-summary-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

### Local Development
```bash
python index.py
```
The application will be available at `http://localhost:5000`

### Using Docker
```bash
docker-compose up --build
```

## API Usage

### Endpoint: `/summarize`
- Method: POST
- Request Body:
```json
{
    "url": "youtube_video_url_here"
}
```
- Response: Returns a JSON object containing the video summary

## Docker Support

The project includes Docker configuration for easy deployment:
- `Dockerfile` for building the container image
- `docker-compose.yml` for orchestrating the container

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT License](LICENSE)

## Acknowledgments

- OpenAI for providing the language model API
- YouTube for the video content
- Flask community for the excellent web framework
