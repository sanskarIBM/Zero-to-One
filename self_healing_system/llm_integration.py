# LLM Integration module (OpenAI example)
import os
import openai

def suggest_locator_with_llm(element_context):
    prompt = f"Suggest a robust XPath for the following element context: {element_context}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
