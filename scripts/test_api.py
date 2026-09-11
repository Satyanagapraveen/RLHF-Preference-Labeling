import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client=Groq(api_key=os.getenv("API_KEY"))

def test_llm_connection():
    response=client.chat.completions.create(
        messages=[{
            "role":"user", "content":"Explain binary Search in One Sentence."
        }],
        model="qwen/qwen3.8-27b",
    )
    print(response.choices[0].message.content)

if __name__ == "__main__":
    test_llm_connection()