# imports

import json
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

# openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
# MODEL = "qwen2.5"

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if api_key and api_key.startswith('sk-proj-') and len(api_key)>10:
    print("API key looks good so far")
else:
    print("There might be a problem with your API key? Please visit the troubleshooting notebook!")
    
MODEL = 'gpt-4o-mini'

#openai = OpenAI()
## Use project info for spend tracking: 
## https://platform.openai.com/settings/organization/usage
## ====================================
openai = OpenAI(organization='org-xs4ecm7YkfNN9ZAa9jPpQvcw', project='proj_cvHNTxzvsy4XU7ZgflSeAcuj',)
print (api_key)

# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# class Website:

#     def __init__(self, url):
#         """
#         Create this Website object from the given url using the BeautifulSoup library
#         """
#         self.url = url
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.content, 'html.parser')
#         self.title = soup.title.string if soup.title else "No title found"
#         for irrelevant in soup.body(["script", "style", "img", "input"]):
#             irrelevant.decompose()
#         self.text = soup.body.get_text(separator="\n", strip=True)

class Website:
    """
    A utility class to represent a Website that we have scraped, now with links and images
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        
        # Initialize empty defaults
        self.text = ""
        self.soup = soup
        self.links_with_images = []
        
        if soup and soup.body:
            # Create a copy for text extraction using a new BeautifulSoup instance
            text_soup = BeautifulSoup(str(soup), 'html.parser')
            for irrelevant in text_soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = text_soup.body.get_text(separator="\n", strip=True)
            
            # Get all links with their associated images
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    img = link.find('img') or link.find_parent().find('img')
                    img_src = img.get('src') if img else "NONE"
                    if img_src != "NONE" and not img_src.startswith(('http://', 'https://')):
                        img_src = requests.compat.urljoin(url, img_src)
                    self.links_with_images.append({'href': href, 'img': img_src})
        
        # Keep the simple links list for backward compatibility
        self.links = [link['href'] for link in self.links_with_images]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"


# Define our system prompt - you can experiment with this later, changing the last sentence to 'Respond in markdown in Spanish."

#system_prompt = "You are an assistant that analyzes the contents of a website \
#and provides a short summary, ignoring text that might be navigation related. \
#Respond in markdown."

# Remove unused system_prompt since we're only using link_system_prompt
link_system_prompt = "You are provided with a list of links and their associated images found on a webpage. \
You are able to decide which of the links would be most relevant to include in an email with articles, links, and images.\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"keywords": "arctic,uk,greenland", "title": "the article title 1", "url": "https://full.url/goes/here/blog/post/1", "image": "https://full.url/goes/here/image1.jpg"},
        {"keywords": "co2,melt,storm", "title": "the article title 2", "url": "https://another.full.url/blog/post/2", "image": "NONE"}
    ]
}
"""

# A function that writes a User Prompt that asks for summaries of websites:

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links and images on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for an email with environment and climate news, respond with the keywords (from the title), title, full https URL, and associated image URL in JSON format. \
If there is no image, use 'NONE' as the image value. Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links and Images:\n"
    user_prompt += "\n".join([f"Link: {link['href']}, Image: {link['img']}" for link in website.links_with_images])
    return user_prompt

# See how this function creates exactly the format above

def get_links(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
      ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)

# Remove unused summarize() and messages_for() functions since we're only using get_links()

# Main execution code
targetUrl = "https://www.theguardian.com/environment/climate-crisis"

print(f"Started")  
print(f"creating summary for {targetUrl}...")  

# HTML template for the email
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        .article-container {{
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
        }}
        .article-image {{
            width: 120px;
            height: 90px;
            object-fit: cover;
            margin-right: 15px;
        }}
        .article-content {{
            flex: 1;
        }}
        .article-title {{
            font-size: 18px;
            margin: 0 0 5px 0;
            color: #333;
        }}
        .article-meta {{
            font-size: 12px;
            color: #666;
        }}
        @media (max-width: 600px) {{
            .article-container {{
                margin-bottom: 15px;
            }}
            .article-image {{
                width: 100px;
                height: 75px;
            }}
            .article-title {{
                font-size: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="news-container">
        {articles}
    </div>
</body>
</html>
"""

article_template = """
    <div class="article-container">
        <img src="{image}" class="article-image" onerror="this.src='https://placehold.co/120x90?text=No+Image'">
        <div class="article-content">
            <h2 class="article-title"><a href="{url}">{title}</a></h2>
            <div class="article-meta">Keywords: {keywords}</div>
        </div>
    </div>
"""

# Replace the OpenAI summary generation with HTML template population
def generate_html_summary(summary_data):
    articles_html = []
    for link in summary_data['links']:
        article_html = article_template.format(
            image=link['image'] if link['image'] != 'NONE' else 'https://placehold.co/120x90?text=No+Image',
            url=link['url'],
            title=link['title'],
            keywords=link['keywords']
        )
        articles_html.append(article_html)
    
    return html_template.format(articles='\n'.join(articles_html))

# Replace the existing summary generation code
summary = get_links(targetUrl)
html_content = generate_html_summary(summary)


# Create results directory if it doesn't exist
results_dir = "results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Generate filename with current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = os.path.join(results_dir, f"links_{timestamp}.json")

# Write summary to file - convert dict to JSON string
with open(filename, "w") as f:
    f.write(json.dumps(summary, indent=2))

print(f"Summary saved to {filename}")

# The rest of the email sending code remains the same, but we don't need to convert from markdown
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
sender_email = os.getenv('SENDER_EMAIL')
email_password = os.getenv('EMAIL_APP_PASSWORD')
receiver_email = os.getenv('RECEIVER_EMAIL')


message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = f"News Summary - {timestamp}"

# Add HTML content directly
message.attach(MIMEText(html_content, "html"))

# Send email via Gmail SMTP
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, email_password)
        server.send_message(message)
    print(f"Summary emailed to {receiver_email}")
except Exception as e:
    print(f"Failed to send email: {str(e)}")
