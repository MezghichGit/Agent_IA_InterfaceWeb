# agent.py
# Agent simple avec 3 outils (tools).
# C'est le LLM qui décide quel outil appeler ; notre code se contente de l'exécuter.
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

# ---------- Connexion à Azure OpenAI ----------
load_dotenv()
client = OpenAI(
    base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/openai/v1/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)
deployment = os.environ["CHAT_DEPLOYMENT"]


# ---------- 1. Les 3 outils : de simples fonctions Python ----------
# Données fictives, pour l'exercice
CLIENTS = {
    "banque horizon": {"secteur": "Banque", "ville": "Lyon", "projet": "Migration cloud + SOC 24/7", "budget_euros": 4200000},
    "energia nord": {"secteur": "Énergie", "ville": "Lille", "projet": "Maintenance prédictive IoT", "budget_euros": 2800000},
    "saint-lumière": {"secteur": "Santé", "ville": "Bordeaux", "projet": "Dossier patient informatisé", "budget_euros": 3500000},
}

# Taux figés pour l'exercice (1 euro = ...)
TAUX = {"USD": 1.08, "GBP": 0.85, "XOF": 655.957, "MAD": 10.9}


def infos_client(nom):
    """Outil 1 : renvoie la fiche d'un client."""
    for cle, fiche in CLIENTS.items():
        if cle in nom.lower() or nom.lower() in cle:
            return json.dumps(fiche, ensure_ascii=False)
    return "Client inconnu. Clients connus : " + ", ".join(CLIENTS)


def convertir_euros(montant, devise):
    """Outil 2 : convertit un montant en euros vers une autre devise."""
    devise = devise.upper()
    if devise not in TAUX:
        return "Devise inconnue. Devises possibles : " + ", ".join(TAUX)
    return f"{montant} EUR = {round(montant * TAUX[devise], 2)} {devise}"


def date_du_jour():
    """Outil 3 : renvoie la date d'aujourd'hui (le LLM ne la connaît pas)."""
    return datetime.now().strftime("%d/%m/%Y")


OUTILS = {
    "infos_client": infos_client,
    "convertir_euros": convertir_euros,
    "date_du_jour": date_du_jour,
}


# ---------- 2. La description des outils, envoyée au LLM ----------
# Le LLM ne voit pas le code : il ne voit que ces descriptions.
DESCRIPTIONS = [
    {"type": "function", "function": {
        "name": "infos_client",
        "description": "Donne la fiche d'un client d'Atos : secteur, ville, projet, budget en euros.",
        "parameters": {
            "type": "object",
            "properties": {"nom": {"type": "string", "description": "Nom du client"}},
            "required": ["nom"],
        },
    }},
    {"type": "function", "function": {
        "name": "convertir_euros",
        "description": "Convertit un montant en euros vers USD, GBP, XOF ou MAD.",
        "parameters": {
            "type": "object",
            "properties": {
                "montant": {"type": "number", "description": "Montant en euros"},
                "devise": {"type": "string", "description": "Devise cible, ex : USD"},
            },
            "required": ["montant", "devise"],
        },
    }},
    {"type": "function", "function": {
        "name": "date_du_jour",
        "description": "Donne la date d'aujourd'hui.",
        "parameters": {"type": "object", "properties": {}},
    }},
]


# ---------- 3. La boucle de l'agent ----------
SYSTEM_PROMPT = "Tu es un assistant commercial d'Atos. Utilise les outils pour répondre. Réponds en français."


def executer_agent(messages):

    print("messages au debut  :", messages,"\n")
    """Fait travailler l'agent sur la conversation `messages`.
    Renvoie la réponse finale et la liste des outils utilisés."""
    outils_utilises = []

    for etape in range(5):  # garde-fou : 5 étapes maximum

        reponse = client.chat.completions.create(
            model=deployment, messages=messages, tools=DESCRIPTIONS)
        message = reponse.choices[0].message

        print("message de lappel LLM  :", message)  # je veux savoir si mon LLM  commence à rédiger la réponse ou s'il demande un outil
        print("message.tool_calls  :", message.tool_calls) # savoir c'est l'outils choisi

        # Cas 1 : le LLM n'a plus besoin d'outil -> il répond
        if not message.tool_calls:
            messages.append({"role": "assistant", "content": message.content})
            return message.content, outils_utilises

        # Cas 2 : le LLM demande un ou plusieurs outils -> on les exécute
        messages.append(message)
        for appel in message.tool_calls:
            nom_outil = appel.function.name
            arguments = json.loads(appel.function.arguments)
            print(f"   [outil] {nom_outil}({arguments})")

            resultat = OUTILS[nom_outil](**arguments)
            print(f"   [résultat] {resultat}")
            outils_utilises.append({"outil": nom_outil, "arguments": arguments, "resultat": resultat})

            # On renvoie le résultat au LLM avec le rôle "tool"
            messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})

    return "Désolé, je n'ai pas pu terminer : trop d'étapes.", outils_utilises


# ---------- 4. Le programme dans le terminal ----------
# Ce bloc s'exécute avec "python agent.py", mais PAS quand app.py fait "from agent import ..."
if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("Pose une question à l'agent (tape quit pour quitter).")
    print("Exemple : Quel est le budget de Banque Horizon en dollars ?\n")

    while True:
        question = input("Vous > ").strip()
        if question.lower() == "quit":
            break
        if not question:
            continue
        messages.append({"role": "user", "content": question})

        reponse, outils = executer_agent(messages)
        print("\nAssistant >", reponse, "\n")
