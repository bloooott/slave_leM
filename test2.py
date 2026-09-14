import ollama
import json

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_offers",
            "description": "Recherche des offres d'emploi dans la base de données. Utilise TOUJOURS min_score=0 et limit=10 si l'utilisateur ne précise rien.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_score": {"type": "number", "description": "Score de pertinence minimum (0 à 1). Mets 0 si non précisé."},
                    "location": {"type": "string", "description": "Filtrer par localisation (ex: Paris). Laisse vide si non précisé."},
                    "keyword": {"type": "string", "description": "Mot-clé à chercher dans titre/description. Laisse vide si non précisé."},
                    "limit": {"type": "integer", "description": "Nombre max de résultats. Mets 10 si non précisé."},
                },
            },
        },
    },
]

SYSTEM_PROMPT = """Tu es un agent qui DOIT utiliser des outils, tu ne réponds JAMAIS directement en texte à une question sur des offres d'emploi.

Règle stricte : dès que l'utilisateur pose une question sur des offres d'emploi, des statistiques,
ou des données, appelle IMMÉDIATEMENT l'outil approprié avec des valeurs par défaut raisonnables
(min_score=0, limit=10, pas de filtre location/keyword si non précisé). NE POSE JAMAIS de question
de clarification avant d'appeler l'outil. Tu peux affiner après avoir vu les premiers résultats.

Ne réponds jamais avec des informations inventées. Base-toi uniquement sur le résultat des outils."""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "dis moi quelles sont les dernières offres d'emploi"},
]

print("Envoi de la requête à Ollama...")
response = ollama.chat(
    model="qwen2.5:7b",
    messages=messages,
    tools=TOOLS,
)

print("\n=== RÉPONSE BRUTE ===")
print(response["message"])

print("\n=== tool_calls présents ? ===")
print(response["message"].get("tool_calls"))