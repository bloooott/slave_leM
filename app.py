import streamlit as st
import ollama
import json
from agent.tools import TOOLS, TOOL_FUNCTIONS

MODEL_NAME = "qwen2.5:7b"  # ou qwen2.5:3b si tu veux tester la vitesse GPU

st.set_page_config(page_title="Job Agent", page_icon="💼")
st.title("💼 Assistant recherche d'emploi (local, Ollama)")

SYSTEM_PROMPT = """Tu es un agent qui DOIT utiliser des outils, tu ne réponds JAMAIS directement en texte à une question sur des offres d'emploi.

Règle stricte : dès que l'utilisateur pose une question sur des offres d'emploi, des statistiques,
ou des données, appelle IMMÉDIATEMENT l'outil approprié avec des valeurs par défaut raisonnables
(min_score=0, limit=10, pas de filtre location/keyword si non précisé). NE POSE JAMAIS de question
de clarification avant d'appeler l'outil. Tu peux affiner après avoir vu les premiers résultats.

Ne réponds jamais avec des informations inventées. Base-toi uniquement sur le résultat des outils.

Une fois les résultats obtenus, présente-les en français sous forme de liste claire avec titre,
entreprise, score de pertinence et lien. Ne lance force_refresh que si l'utilisateur le demande explicitement."""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages:
    if msg["role"] in ("user", "assistant") and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def call_agent(user_input: str) -> str:
    st.session_state.messages.append({"role": "user", "content": user_input})

    while True:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=st.session_state.messages,
            tools=TOOLS,
        )
        msg = response["message"]
        st.session_state.messages.append(msg)

        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            return msg.get("content", "")

        for call in tool_calls:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            func = TOOL_FUNCTIONS.get(name)
            try:
                result = func(**args) if func else {"error": "Fonction inconnue"}
            except Exception as e:
                result = {"error": str(e)}

            st.session_state.messages.append({
                "role": "tool",
                "content": json.dumps(result, ensure_ascii=False, default=str),
            })

user_input = st.chat_input("Pose une question sur les offres d'emploi...")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Recherche en cours..."):
            answer = call_agent(user_input)
        st.markdown(answer)