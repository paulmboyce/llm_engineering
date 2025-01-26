# Website Summarizer (TypeScript)

A TypeScript application that fetches web content, generates summaries using Ollama's local LLM, saves them locally, and emails the results.

## Features

- Scrapes website content using Cheerio
- Generates summaries using Ollama's Qwen 2.5 model
- Saves summaries in both markdown and HTML formats
- Emails the summary with proper HTML formatting
- Handles various website layouts and structures
- Written in TypeScript for better type safety and developer experience

## Prerequisites

- Node.js 18 or higher
- Ollama running locally with Qwen 2.5 model installed
- Gmail account with App Password configured

## Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Configure your .env file with:
```
SENDER_EMAIL=your-email@gmail.com
EMAIL_APP_PASSWORD=your-gmail-app-password
```

## Gmail Setup

To use Gmail for sending summaries:

1. Go to your Google Account settings
2. Navigate to Security > 2-Step Verification
3. Scroll to App Passwords
4. Generate a new app password
5. Copy the password to your .env file

## Usage

1. Build the project:
```bash
npm run build
```

2. Run the application:
```bash
npm start
```

To modify the target URL, edit the `targetUrl` variable in `src/app.ts`.

## Development

- Start in development mode with auto-reload:
```bash
npm run dev
```

## Project Structure

```
typescript/
├── src/
│   └── app.ts          # Main application code
├── dist/               # Compiled JavaScript
├── results/            # Generated summaries
├── package.json        # Project dependencies
├── tsconfig.json       # TypeScript configuration
└── .env               # Environment variables
```

## Output

- Summaries are saved in `results/summary_YYYY-MM-DD_HH-MM-SS.md`
- HTML versions are saved in `results/summary_YYYY-MM-DD_HH-MM-SS.html`
- Emails are sent in HTML format with proper markdown rendering

## Dependencies

- axios: HTTP client
- cheerio: HTML parsing
- date-fns: Date formatting
- dotenv: Environment variable management
- markdown-it: Markdown to HTML conversion
- nodemailer: Email sending
- ollama: LLM API interface

## Error Handling

The application includes robust error handling for:
- Website fetching issues
- LLM connection problems
- File system operations
- Email sending failures

## Notes

- The application uses Ollama's local API endpoint
- Website content is cleaned of scripts, styles, and other irrelevant elements
- Summaries are generated in markdown format for better readability
- The application requires Ollama to be running locally (`ollama serve`)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 