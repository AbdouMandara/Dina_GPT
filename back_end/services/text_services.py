import httpx
import json
from core.config import Settings

settings = Settings()
HF_TOKEN = settings.token

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

async def query_hf_api(payload: dict):
    """
    Sends a request to the Hugging Face API (Asynchronous).
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Unexpected error in text_services: {str(e)}")

async def generate_word_data(word: str):
    """
    Génère des données structurées pour l'apprentissage d'un mot (Traduction, Définition, Phrases).
    """
    system_prompt = (
        "Tu es un assistant professeur d'anglais expert. Pour chaque mot donné, tu dois répondre UNIQUEMENT au format JSON avec la structure suivante :\n"
        "{\n"
        "  \"word\": \"le mot original\",\n"
        "  \"phonetic\": \"transcription phonétique IPA (ex: /ɪˈfɛmərəl/)\",\n"
        "  \"part_of_speech\": \"nature du mot (ex: noun, verb, adjective)\",\n"
        "  \"translation\": \"traduction principale en français\",\n"
        "  \"definition\": \"définition précise et élégante en français\",\n"
        "  \"synonyms\": [\"synonyme 1\", \"synonyme 2\", \"synonyme 3\"],\n"
        "  \"formatted_message\": \"Résumé court du mot et de son sens\",\n"
        "  \"examples\": [\n"
        "    {\"en\": \"phrase d'exemple 1 en anglais\", \"fr\": \"traduction 1\"},\n"
        "    {\"en\": \"phrase d'exemple 2 en anglais\", \"fr\": \"traduction 2\"},\n"
        "    {\"en\": \"phrase d'exemple 3 en anglais\", \"fr\": \"traduction 3\"}\n"
        "  ]\n"
        "}\n"
        "Réponds directement avec le JSON, sans explications. Tout le texte explicatif doit être en français."
    )

    
    payload = {
        "messages": [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": f"Traite le mot suivant : {word}"
            }
        ],
        "model": "google/gemma-4-26B-A4B-it:novita"
    }

    response_json = await query_hf_api(payload)
    content = response_json["choices"][0]["message"]["content"]
    
    # Nettoyage du contenu si l'IA ajoute des balises markdown ```json
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
        
    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError:
        raise Exception(f"Erreur de formatage JSON de l'IA : {content}")

if __name__ == "__main__":
    import asyncio
    
    async def test():
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this image in one sentence."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
                            }
                        }
                    ]
                }
            ],
            "model": "google/gemma-4-26B-A4B-it:novita"
        }
        try:
            response = await query_hf_api(payload)
            print(response["choices"][0]["message"])
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(test())
