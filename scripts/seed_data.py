import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Label
from database import SessionLocal
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client=Groq(api_key=os.getenv("API_KEY"))

def generate_response(prompt:str,temp:float)->str:
    response=client.chat.completions.create(
        messages=[{"role":"user", "content":prompt}],
        model=os.getenv("GROQ_MODEL"),
        temperature=temp,
        max_tokens=250
    )
    return response.choices[0].message.content

def seed_database():
    db=SessionLocal()
    try:
        script_dir=os.path.dirname(os.path.abspath(__file__))
        json_path=os.path.join(script_dir,'seed_prompts.json')

        with open(json_path,'r') as file:
            prompt_data=json.load(file)

        for item in prompt_data:
            prompt_text=item["prompt"]
            category=item["category"]
            print(f"Generating responses for: {prompt_text[:30]}...")
            response_a=generate_response(prompt_text,temp=0.2)
            response_b=generate_response(prompt_text,temp=0.8)
            new_label=Label(
                prompt=prompt_text,
                response_a=response_a,
                response_b=response_b,
                category=category,
                annotator_id="system",

            )
            db.add(new_label)
        db.commit()
        print("Successfully seeded all prompt pairs into the database.")
    except Exception as e:
        db.rollback()
        print(f"An error occured:{e}")
    finally:
        db.close()

if __name__=="__main__":
    seed_database()


