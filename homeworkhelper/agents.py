import os
import openai
import streamlit as st

# ✅ Initialize OpenAI client correctly
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clarification_agent(question):
    """Clarifies a student's question."""
    response = client.chat.completions.create(  # ✅ New API syntax
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"A student asked: '{question}'\n\nIs the question clear? If not, ask for more details:"}
        ]
    )
    return response.choices[0].message.content.strip()  # ✅ Correct content extraction

def solution_agent(question):
    """Provides a detailed solution to a homework question."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Provide a detailed solution to the following homework question:\n\n{question}\n\nSolution:"}
        ]
    )
    return response.choices[0].message.content.strip()

def quality_assurance_agent(solution):
    """Reviews a solution for accuracy and suggests improvements."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Review the following solution for accuracy and completeness. Suggest improvements if necessary:\n\n{solution}\n\nReview:"}
        ]
    )
    return response.choices[0].message.content.strip()

def concise_answer_agent(solution):
    """Provides a concise summary of a detailed solution."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Provide a concise summary of the following detailed solution:\n\n{solution}\n\nConcise Summary:"}
        ]
    )
    return response.choices[0].message.content.strip()