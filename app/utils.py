import re

def clean_text(text):
    #Remove HTML tags
    text = re.sub(r'<[^>]*?>','',text)
    #Remove URLS
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    #REmove Special Characters
    text= re.sub(r'[^a-zA-Z0-9 ]', '', text)
    # Replace multiple space with single space
    text=re.sub(r'\s{2,}',' ',text)
    # Trim leading and trailing whitespace
    text = text.strip()
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text
    
def clean_portfolio_text(text):
    """
    Cleans the input text by removing special characters, extra spaces, and normalizing the format.
    """
    # Remove unwanted characters and normalize text
    text = re.sub(r'[^\w\s,.:/]', '', text)  # Remove special characters except common punctuation
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = text.strip()  # Trim leading and trailing spaces
    return text