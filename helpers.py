from langchain.llms import OpenAI
from pypdf import PdfReader
import pandas as pd
import re
from langchain.prompts import PromptTemplate
import openai
import os
from dotenv import find_dotenv, load_dotenv

# Load OpenAI API key from .env file
load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to extract text from PDF file
def get_pdf_text(pdf_doc: str) -> str:
    text = ""
    try:
        pdf_reader = PdfReader(pdf_doc)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading {pdf_doc}: {e}")
    return text

# Function to extract structured data from text
def extract_data(pages_data: str) -> dict:
    template = """Extract all the following values: Invoice ID, DESCRIPTION, Issue Date, 
    UNIT PRICE, AMOUNT, Bill For, From and Terms from: {pages}

    Expected output: remove any dollar symbols {'Invoice ID': '1001329', 'DESCRIPTION': 'ITEM', 
    'Issue Date': '5/4/2023', 'UNIT PRICE': '1100.00', 'AMOUNT': '1100.00', 'Bill For': 'james', 
    'From': 'excel company', 'Terms': 'pay this now'}"""
    
    prompt_template = PromptTemplate(input_variables=["pages"], template=template)
    llm = OpenAI(temperature=0.7)
    
    try:
        response = llm(prompt_template.format(pages=pages_data))
        match = re.search(r'{(.+)}', response, re.DOTALL)
        if match:
            extracted_text = match.group(1)
            return eval('{' + extracted_text + '}')  # Safeguard against malicious input
    except Exception as e:
        print(f"Error extracting data: {e}")
    
    return {}

# Function to create a DataFrame from the extracted PDF data
def create_docs(user_pdf_list: list[str]) -> pd.DataFrame:
    df = pd.DataFrame(columns=[
        'Invoice ID', 'DESCRIPTION', 'Issue Date', 
        'UNIT PRICE', 'AMOUNT', 'Bill For', 'From', 'Terms'
    ])
    
    for filename in user_pdf_list:
        print(f"Processing: {filename}")
        raw_data = get_pdf_text(filename)

        if raw_data:
            extracted_data = extract_data(raw_data)
            if extracted_data:
                df = pd.concat([df, pd.DataFrame([extracted_data])], ignore_index=True)
            else:
                print("No data extracted.")
        else:
            print("No raw data found.")

    print("********************DONE***************")
    return df
