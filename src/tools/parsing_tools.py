import re

def extract_numerical_value(text):
    # Regular expression to match a sequence of digits that may contain a decimal point
    match = re.search(r'\d+\.\d+|\d+', text)
    if match:
        return float(match.group())
    else:
        return None