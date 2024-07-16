import re
from langchain_openai import ChatOpenAI

def extract_numerical_value(text):
    return text
    # Regular expression to match a sequence of digits that may contain a decimal point
    print(f"extacting numerical value from: {text}")
    match = re.search(r'\b\d{1,3}(?:[.,]\d{3})*(?:\.\d+)?\b', text)
    if match:
        return (match.group())
    else:
        return None

