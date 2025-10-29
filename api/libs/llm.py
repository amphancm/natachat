import requests
from sqlalchemy.orm import Session
from libs.db import SessionLocal
from schemas.models import Setting

# Import Gemini SDK
from google import genai
from google.genai.types import GenerateContentConfig

def load_setting(db: Session):
    return db.query(Setting).first()

def get_llm_response(prompt: str) -> str:
    db = SessionLocal()
    try:
        setting = load_setting(db)
        if not setting:
            return "No setting found"

        print(f"""
        Current Setting:
        isLocal: {setting.isLocal}
        isApi: {setting.isApi}
        apiKey: {setting.apiKey}
        domainName: {setting.domainName}
        modelName: {setting.modelName}
        temperature: {setting.temperature}
        systemPrompt: {setting.systemPrompt}
        """)

        if setting.isLocal:
            return f"Local model response to: {prompt}"

        elif setting.isApi and setting.domainName == "huggingface":
            url = f"https://api-inference.huggingface.co/models/{setting.modelName}"
            headers = {"Authorization": f"Bearer {setting.apiKey}"}

            full_prompt = prompt
            if setting.systemPrompt:
                full_prompt = f"{setting.systemPrompt}\n\nUser: {prompt}"

            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 512,
                    "temperature": setting.temperature or 0.7
                }
            }

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                return f"HuggingFace API Error: {response.text}"

            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"].replace(full_prompt, "").strip()

            if isinstance(data, dict) and "error" in data:
                return f"HuggingFace API Error: {data['error']}"

            return str(data)

        elif setting.isApi and setting.domainName == "google":
            client = genai.Client(api_key=setting.apiKey)

            full_prompt = prompt
            if setting.systemPrompt:
                full_prompt = f"{setting.systemPrompt}\n\nUser: {prompt}"
            response = client.models.generate_content(
                model=setting.modelName,
                contents=full_prompt,
                config=GenerateContentConfig(
                    temperature=setting.temperature or 0.7,
                ),
            )
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            else:
                return "Gemini: No text returned from model"


        else:
            return "No model configured"

    finally:
        db.close()
