from string import ascii_uppercase
import random
import pathlib
import textwrap
from dotenv import load_dotenv
import os

import google.generativeai as genai
load_dotenv()

def generate_answer(question):
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
        question: {question}
        answer(be brief until asked): 
    """
    response = model.generate_content(prompt)
    print(response)
    return response.text

def generate_unique_code(code_length, rooms):
    while True:
        code = ""
        for _ in range(code_length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    
    return code