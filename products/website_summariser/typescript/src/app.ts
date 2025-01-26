import axios from 'axios';
import * as cheerio from 'cheerio';
import dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';
import { format } from 'date-fns';
import nodemailer from 'nodemailer';
import MarkdownIt from 'markdown-it';
import ollama from 'ollama';

// Load environment variables
dotenv.config();


const MODEL = "qwen2.5";

// HTTP request headers
const headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
};

class Website {
    url: string;
    title: string;
    text: string;

    constructor(url: string) {
        this.url = url;
        this.title = '';
        this.text = '';
    }

    async initialize(): Promise<void> {
        try {
            const response = await axios.get(this.url, { headers });
            const $ = cheerio.load(response.data);
            
            this.title = $('title').text() || 'No title found';
            
            // Remove irrelevant elements
            $('script, style, img, input').remove();
            
            this.text = $('body')
                .text()
                .replace(/\s+/g, ' ')
                .trim();
        } catch (error) {
            console.error('Error fetching website:', error);
            throw error;
        }
    }
}

// System prompt
const systemPrompt = `You are an assistant that analyzes the contents of a website \
and provides a short summary, including the titles and image links of posts/articles that might be navigation related. \
Respond in markdown.`;

function createUserPrompt(website: Website): string {
    return `You are looking at a website titled ${website.title}
The contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.

${website.text}`;
}

// Update the message type definition
type ChatMessage = {
    role: 'system' | 'user' | 'assistant';
    content: string;
}

function createMessages(website: Website): ChatMessage[] {
    return [
        { role: "system", content: systemPrompt },
        { role: "user", content: createUserPrompt(website) }
    ];
}

async function summarize(url: string): Promise<string> {

    const website = new Website(url);
    await website.initialize();
    
    console.log(`website text (from Cheerio): \n ${website.text}`);
    
    try {
        const response = await ollama.chat({
            model: MODEL,
            messages: createMessages(website)
        });

        const content = response.message.content;
        if (!content) {
            throw new Error('No content received from LLM');
        }
        
        return content;
    } catch (error) {
        console.error('Error calling Ollama:', error);
        if (error instanceof Error && (error as any).message.includes('ECONNREFUSED')) {
            throw new Error('Could not connect to Ollama. Please ensure Ollama is running on port 11434');
        }
        throw error;
    }
}

async function saveToFile(content: string, directory: string, extension: string): Promise<string> {
    if (!fs.existsSync(directory)) {
        fs.mkdirSync(directory, { recursive: true });
    }

    const timestamp = format(new Date(), 'yyyy-MM-dd_HH-mm-ss');
    const filename = path.join(directory, `summary_${timestamp}.${extension}`);
    
    fs.writeFileSync(filename, content);
    return filename;
}

async function sendEmail(summary: string, timestamp: string): Promise<void> {
    const md = new MarkdownIt();
    const htmlContent = md.render(summary);
    
    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: process.env.SENDER_EMAIL,
            pass: process.env.EMAIL_APP_PASSWORD
        }
    });

    const mailOptions = {
        from: process.env.SENDER_EMAIL,
        to: "paulmboyce@gmail.com", // Consider making this configurable
        subject: `Website Summary - ${timestamp}`,
        html: htmlContent
    };

    try {
        await transporter.sendMail(mailOptions);
        console.log('Email sent successfully');
    } catch (error) {
        console.error('Error sending email:', error);
        throw error;
    }
}

async function main() {
    const targetUrl = "https://www.theguardian.com/environment/climate-crisis";
    
    console.log('Started');
    console.log(`Creating summary for ${targetUrl}...`);

    try {
        const summary = await summarize(targetUrl);
        console.log(`Summarized website (by LLM): \n ${summary}`);

        const resultsDir = path.join(__dirname, '..', 'results');
        
        // Save markdown version
        const mdFilename = await saveToFile(summary, resultsDir, 'md');
        console.log(`Summary saved to ${mdFilename}`);

        // Save HTML version
        const md = new MarkdownIt();
        const htmlContent = md.render(summary);
        const htmlFilename = await saveToFile(htmlContent, resultsDir, 'html');
        console.log(`HTML version saved to ${htmlFilename}`);

        // Send email
        const timestamp = format(new Date(), 'yyyy-MM-dd_HH-mm-ss');
        await sendEmail(summary, timestamp);
        
    } catch (error) {
        console.error('Error in main process:', error);
    }
}

main(); 