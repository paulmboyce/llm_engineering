import axios from 'axios';
import * as cheerio from 'cheerio';

/**
 * Function to fetch and parse a webpage.
 * @param url The URL of the webpage to fetch.
 */
const scrapePage = async (url: string) => {
    try {
        // Fetch the HTML of the page
        const response = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });

        if (!response.data) {
            throw new Error('No data received from the server');
        }

        console.log('Response type:', typeof response.data);
        console.log('Response data:', response.data.substring(0, 200)); // Show first 200 chars

        // Load the HTML into cheerio        
        const $ = cheerio.load(response.data.toString());  // Ensure we're passing a string

        // Extract the title of the page
        const title = $('title').text();
        
        // Extract all text from the body of the page
        const bodyText = $('body')
            .clone()    // Create a clone to not modify the original
            .find('script, path')    // Find all script and path tags
            .remove()    // Remove them
            .end()    // Go back to body
            .text()    // Get the remaining text
            .trim();    // Remove extra whitespace

        // Extract full HTTPS links to IMG images
        const imgLinks: string[] = [];
        $('img').each((_, element) => {
            const imgSrc = $(element).attr('src');
            if (imgSrc) {
                // Resolve image URLs to full HTTPS links
                const fullUrl = new URL(imgSrc, url).href;
                imgLinks.push(fullUrl);
            }
        });

        return {
            title,
            bodyText,
            imgLinks,
        };
    } catch (error: any) {
        console.error(`Error fetching the page: ${error.message}`);
        return null;
    }
};

// Example usage
const urlToScrape = 'https://www.theguardian.com/environment/climate-crisis'; // Replace with the URL you want to scrape
scrapePage(urlToScrape).then(result => {
    if (result) {
        console.log('Title:', result.title);
        console.log('Body Text:', result.bodyText);
        console.log('Image Links:', result.imgLinks);
    }
});