from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def ai_reply(conversation):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=conversation
    )
    return response.choices[0].message.content
