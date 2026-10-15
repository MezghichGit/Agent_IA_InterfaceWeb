# app.py
# TP : une interface web de type ChatGPT pour notre agent.
#   - le navigateur affiche la page templates/index.html
#   - quand on envoie une question, la page appelle /api/chat
#   - le serveur fait travailler l'agent (agent.py) et renvoie la réponse en JSON
from flask import Flask, jsonify, render_template, request
from openai import OpenAIError

from agent import SYSTEM_PROMPT, executer_agent

app = Flask(__name__)


# ---------- Route 1 : la page web ----------
@app.get("/")
def accueil():
    return render_template("index.html")


# ---------- Route 2 : l'API de chat ----------
@app.post("/api/chat")
def chat():
    donnees = request.get_json(silent=True) or {}
    historique = donnees.get("historique", [])

    # Le navigateur envoie toute la conversation (le LLM n'a pas de mémoire).
    # Sécurité : on ne fait pas confiance au navigateur. On ne garde que les rôles
    # "user" et "assistant" (pas de faux message "system"), les 20 derniers messages,
    # et des textes de 2 000 caractères maximum.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for message in historique[-20:]:
        if message.get("role") in ("user", "assistant") and isinstance(message.get("content"), str):
            messages.append({"role": message["role"], "content": message["content"][:2000]})

    if messages[-1]["role"] != "user":
        return jsonify({"erreur": "La conversation doit se terminer par une question."}), 400

    try:
        reponse, outils = executer_agent(messages)
    except OpenAIError as erreur:
        print("Erreur Azure OpenAI :", erreur)  # le détail reste côté serveur
        return jsonify({"erreur": "Le service IA ne répond pas. Réessayez dans un instant."}), 502

    return jsonify({"reponse": reponse, "outils": outils})


if __name__ == "__main__":
    # debug=True : rechargement automatique quand on modifie le code. JAMAIS en production.
    app.run(debug=True, port=5000)
