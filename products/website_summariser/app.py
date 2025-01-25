# imports

import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

ollama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
MODEL = "qwen2.5"

# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:

    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)




# Define our system prompt - you can experiment with this later, changing the last sentence to 'Respond in markdown in Spanish."

#system_prompt = "You are an assistant that analyzes the contents of a website \
#and provides a short summary, ignoring text that might be navigation related. \
#Respond in markdown."

system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, including the titles and image links of posts/articles that might be navigation related. \
Respond in markdown."


# A function that writes a User Prompt that asks for summaries of websites:

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt


# See how this function creates exactly the format above

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]


def summarize(url):
    website = Website(url)
    response = ollama_via_openai.chat.completions.create(
        model = MODEL,
        messages = messages_for(website)
    )
    return response.choices[0].message.content


    
# TESTING:
# ====================
# Let's try one out. Change the website and add print statements to follow along.
#edWebsite = Website("https://edwarddonner.com/")
#edWebsite = Website("https://ft.com/")
edWebsite = Website("https://www.theguardian.com/environment/climate-crisis")

#print(edWebsite.title)
#print(edWebsite.text)
#print(user_prompt_for(edWebsite))
#print(messages_for(edWebsite))

#targetUrl = "https://edwarddonner.com"
targetUrl = "https://www.theguardian.com/environment/climate-crisis"

print(f"Started")  
print(f"creating summary for {targetUrl}...")  

summary = summarize(targetUrl)
#print(summary)

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
