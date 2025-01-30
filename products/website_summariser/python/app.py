# imports

import json
import os
import requests
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
    A utility class to represent a Website that we have scraped, now with links
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"


# Define our system prompt - you can experiment with this later, changing the last sentence to 'Respond in markdown in Spanish."

#system_prompt = "You are an assistant that analyzes the contents of a website \
#and provides a short summary, ignoring text that might be navigation related. \
#Respond in markdown."

# Remove unused system_prompt since we're only using link_system_prompt
link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a an email with articles, and links to pages.\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"keywords": "arctic,uk,greenland", "title": "the article title 1", "url": "https://full.url/goes/here/blog/post/1"},
        {"keywords": "co2,melt,storm", "title": "the article title 2": "url": "https://another.full.url/blog/post/2"}
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
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for an email with environment and climate news, respond with the keywords (from the title), title and full https URL in JSON format. \
Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
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

summary = get_links(targetUrl)
print(summary)

system_prompt_for_summary = "You are an assistant that analyzes the links, titles and keywords of a posts on a webpage \
and creates a short summary of the webpage containing all the links and titles and keywords for an email to a client. Respond in markdown."
 
user_prompt_for_summary = "Here are the links, titles and keywords of the posts on the webpage: \n"
user_prompt_for_summary += "\n".join([f"{link['title']} - {link['keywords']} - {link['url']}" for link in summary['links']])    

print(f"-----------------------------------------------\n\n")
print(f"System prompt for summary: {system_prompt_for_summary}")
print(f"-----------------------------------------------\n\n")
print(f"User prompt for summary: {user_prompt_for_summary}")
print(f"-----------------------------------------------\n\n")

print(f"About to call openai.chat.completions.create....\n\n")
summary_response = openai.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt_for_summary},
        {"role": "user", "content": user_prompt_for_summary}
    ]
)   

summary = summary_response.choices[0].message.content
print(summary)

#summary = "This is a test summary"

from datetime import datetime
import os

# Create results directory if it doesn't exist
results_dir = "results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Generate filename with current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = os.path.join(results_dir, f"summary_{timestamp}.md")

# Write summary to file
with open(filename, "w") as f:
    f.write(summary)

print(f"Summary saved to {filename}")
#display(Markdown(summary))



# Email the summary
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load email credentials from .env file
load_dotenv()


email_password = os.getenv('EMAIL_APP_PASSWORD')
sender_email = os.getenv('SENDER_EMAIL')
receiver_email = "paulmboyce@gmail.com"

print(f"-----------------------------------------------\n\n")
print(f"About to email the summary to {receiver_email}")
print(f"-----------------------------------------------\n\n")

print(f"Loaded email: {sender_email}")
print(f"Password loaded: {'yes' if email_password else 'no'}")

# Create the email message
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = f"Website Summary - {timestamp}"

# Convert markdown to HTML
from markdown import markdown

# Convert the markdown summary to HTML format
html_content = markdown(summary)


# Add summary as email body
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
