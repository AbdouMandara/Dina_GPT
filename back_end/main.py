from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
import os
import uuid
from core.config import Settings
from services.text_services import generate_word_data
from pydantic import BaseModel

# Initialisation
settings = Settings()
HF_TOKEN = settings.token
app = FastAPI(title="ChatBot API")

# Création du dossier statique s'il n'existe pas
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

class ChatRequest(BaseModel):
    prompt: str

class WordRequest(BaseModel):
    word: str

@app.post("/chat")
async def chat(request: ChatRequest):
    payload = {
        "model": "openai/gpt-oss-20b:groq",
        "messages": [
            {
                "role": "user", 
                "content": request.prompt
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"API Error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn-word")
async def learn_word(request: WordRequest):
    try:
        # 1. Obtenir les données textuelles (Traduction, définitions, phrases)
        word_data = await generate_word_data(request.word)
        
        # 2. Retourner la réponse complète (sans audio)
        return {
            "word": word_data.get("word"),
            "phonetic": word_data.get("phonetic"),
            "part_of_speech": word_data.get("part_of_speech"),
            "message": word_data.get("formatted_message"),
            "translation": word_data.get("translation"),
            "definition": word_data.get("definition"),
            "synonyms": word_data.get("synonyms", []),
            "examples": word_data.get("examples", [])
        }

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
