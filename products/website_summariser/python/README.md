# Website Summarizer

A Python application that fetches web content, generates summaries using an LLM (Large Language Model), saves them locally, and emails the results.

## Features

- Scrapes website content using BeautifulSoup
- Generates summaries using Ollama's Qwen 2.5 model
- Saves summaries to markdown files with timestamps
- Emails the summary in HTML format
- Handles various website layouts and structures

## Prerequisites

- Python 3.x
- Ollama running locally with Qwen 2.5 model
- Gmail account with App Password configured

## Installation

1. Clone the repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Set up environment variables:
```
cp .env.example .env
```
4. Run the application:
```
python app.py
```

## Configuration

- The application uses Gmail SMTP for sending emails
- To set up Gmail App Password:
  1. Go to Google Account Settings
  2. Security > 2-Step Verification
  3. App Passwords > Generate new app password
  4. Copy the generated password to .env file

## Usage

1. Update the target URL in app.py:
```python
targetUrl = "https://your-target-website.com"
```

2. Run the application:
```bash
python app.py
```

The application will:
- Fetch the website content
- Generate a summary
- Save it to the `results` directory
- Email the summary to the configured recipient

## Output

- Summaries are saved in `results/summary_YYYY-MM-DD_HH-MM-SS.md`
- Emails are sent in HTML format with proper markdown rendering

## Dependencies

- requests: For HTTP requests
- beautifulsoup4: For HTML parsing
- python-dotenv: For environment variable management
- openai: For LLM API interface
- ipython: For markdown display
- markdown: For converting markdown to HTML

## Notes

- The application uses Ollama's local API endpoint (http://localhost:11434/v1)
- Website content is cleaned of scripts, styles, and other irrelevant elements
- Summaries are generated in markdown format for better readability