from langchain_openai import ChatOpenAI

text_chat = ChatOpenAI(temperature=0, model=model)
text_prompt = f'''
The text below is extracted from financial payslips, answer the question based on the text provided.
Text:
{table_text}

Question:

'''