from typing import Optional
from transformers import AutoTokenizer
import re

BASE_MODEL = "meta-llama/Meta-Llama-3.1-8B"

MIN_TOKENS = 150 # Any less than this, and we don't have enough useful content
MAX_TOKENS = 160 # Truncate after this many tokens. Then after adding in prompt text, we will get to around 180 tokens

MIN_CHARS = 300
CEILING_CHARS = MAX_TOKENS * 7

class Item:
    """
    An Item is a cleaned, curated datapoint of a Product with a Price
    """
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    PREFIX = "Price is $"
    QUESTION = "How much does this cost to the nearest dollar?"
    REMOVALS = ['"Batteries Included?": "No"', '"Batteries Included?": "Yes"', '"Batteries Required?": "No"', '"Batteries Required?": "Yes"', "By Manufacturer", "Item", "Date First", "Package", ":", "Number of", "Best Sellers", "Number", "Product "]

    title: str
    price: float

    token_count: int = 0
    prompt: Optional[str] = None
    include = False

    def __init__(self, data, price):
        self.title = data['title']
        self.price = price
        self.parse_to_prompt(data)

    def scrub_details(self, details):
        """
        Clean up the details string by removing common text that doesn't add value
        """
        for remove in self.REMOVALS:
            details = details.replace(remove, "")
        return details

    def remove_part_numbers(self,text):    
        """
        Remove Part Numbers: The data contains many 8 digit part numbers (a mix of chars and numbers).
        Remove, because:
         (a) they add little value 
         (b) they consume vital tokens (so relate to training price)
         (c) as random strings, they aren't in the model vocab (more token expensive)
         (d) example of improving data quality; should prove in results as more accurate data
         """
        words = text.split(' ')
        select = []
        for word in words:
            # Check if word is less than 7 characters
            if len(word) < 7:
                select.append(word)
            # Otherwise, check if it contains no digits
            elif not any(char.isdigit() for char in word):
                select.append(word)  
        return " ".join(select)

        
    def scrub_text(self, text):
        """
        Clean up the provided text by removing unnecessary characters and whitespace
        Remove likely irrelevant product numbers: words that are 7+ chars and contain numbers
        """
        text = re.sub(r'[:\[\]"{}【】\s]+', ' ', text).strip()
        text = text.replace(" ,", ",").replace(",,,",",").replace(",,",",").replace(".,",".")
        text = self.remove_part_numbers(text)
        return text


    def parse_to_prompt(self, data):
        """
        Parse a datapoint.
        If it fits within the allowed Token range, set include to True.
        """
        description = '\n'.join(data['description'])
        if description:
            description += '\n'
       
        features = '\n'.join(data['features'])
        if features:
            features += '\n'

        
        details = data['details']
        if details:
            details = self.scrub_details(details) + '\n'

        contents = description + features + details
            
        if len(contents) > MIN_CHARS:
            truncated_contents = contents[:CEILING_CHARS]            
            scrubbed_text = f"{self.scrub_text(self.title)}\n{self.scrub_text(truncated_contents)}"
            self.make_prompt_for_viable_text(scrubbed_text)


    def make_prompt_for_viable_text(self, candidate_text):
        '''
        A text is viable for including as a prompt if its token size is between MIN_TOKENS and MAX_TOKENS
        This gives control over data quantity and affects traing costs via token counts. 
        '''
        tokens = self.tokenizer.encode(candidate_text, add_special_tokens=False)
        if len(tokens) > MIN_TOKENS:
            truncated_tokens = tokens[:MAX_TOKENS]
            truncated_text = self.tokenizer.decode(truncated_tokens)
            self.make_prompt(truncated_text)
            self.include = True

    
    def make_prompt(self, text):
        """
        Set the prompt instance variable to be a prompt appropriate for training
        """
        # There are 4 parts:
        # 1) QUESTION: we're training the model to answer e.g "How much does this cost in dollars?" 
        # 2) TEXT: this is the training content text
        # 3) PREFIX: this is the training response format e.g "Price is $"
        # 4) ANSWER: this is the training response value e.g. "$27"
        self.prompt = f"{self.QUESTION}\n\n"
        self.prompt += f"{text}\n\n"
        self.prompt += f"{self.PREFIX}"
        self.prompt += f"{str(round(self.price))}.00"
        self.token_count = len(self.tokenizer.encode(self.prompt, add_special_tokens=False))

    
    def test_prompt(self):
        """
        Return a prompt suitable for testing, with the actual price removed
        """
        return self.prompt.split(self.PREFIX)[0] + self.PREFIX

    
    def __repr__(self):
        """
        Return a String version of this Item
        """
        return f"<{self.title} = ${self.price}>"

        

    
    