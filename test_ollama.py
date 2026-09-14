import ollama
import json

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_offers",
            "description": "Recherche des offres d'emploi dans la base de données selon score minimum, localisation, ou mot-clé.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_score": {"type": "number", "description": "Score de pertinence minimum (0 à 1)"},
                    "location": {"type": "string", "description": "Filtrer par localisation (ex: Paris)"},
                    "keyword": {"type": "string", "description": "Mot-clé à chercher dans titre/description"},
                    "limit": {"type": "integer", "description": "Nombre max de résultats"},
                },
            },
        },
    },
]

messages = [
    {"role": "system", "content": "Tu es un assistant qui aide à trouver des offres d'emploi via des outils. Utilise TOUJOURS l'outil search_offers pour répondre à une question sur les offres, ne réponds JAMAIS avec des informations inventées."},
    {"role": "user", "content": "dis moi quelles sont les dernières offres d'emploi"},
]

print("Envoi de la requête à Ollama...")
response = ollama.chat(
    model="qwen2.5:7b",
    messages=messages,
    tools=TOOLS,
)

print("\n=== RÉPONSE BRUTE ===")
print(json.dumps(response["message"], indent=2, ensure_ascii=False, default=str))

print("\n=== tool_calls présents ? ===")
print(response["message"].get("tool_calls"))