from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, TrainingArguments, Trainer
import torch
from string import ascii_uppercase
import random
import pathlib
import textwrap
from dotenv import load_dotenv
import os

import google.generativeai as genai

load_dotenv()

def generate_summary(dialogue):
    # model_name='google/flan-t5-base'
    # tokenizer = AutoTokenizer.from_pretrained(model_name)
    # instruct_model = AutoModelForSeq2SeqLM.from_pretrained(
    #     "./flan-dialogue-summary-checkpoint", torch_dtype=torch.bfloat16)

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Summarize the following conversation.

    {dialogue}

    Summary:
    """

    response = model.generate_content(prompt)
    print(response)
    return response.text

    # input_ids = tokenizer(prompt, return_tensors="pt").input_ids

    # instruct_model_outputs = instruct_model.generate(
    #     input_ids=input_ids, generation_config=GenerationConfig(max_new_tokens=200, num_beams=1))
    # instruct_model_text_output = tokenizer.decode(
    #     instruct_model_outputs[0], skip_special_tokens=True)
    
    return instruct_model_text_output
