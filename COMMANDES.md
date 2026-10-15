# Commandes à exécuter – Projet 2 : Agent avec 3 outils

Ouvre le dossier `projet2-agent` dans VS Code, puis **Terminal → Nouveau terminal**.

## 1. Créer le fichier .env

Windows (PowerShell) :
```powershell
Copy-Item .env.example .env
```
macOS / Linux :
```bash
cp .env.example .env
```
Ouvre `.env` et remplis `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` et `CHAT_DEPLOYMENT`.

## 2. Créer et activer l'environnement virtuel

```bash
python -m venv .venv
```
Windows (PowerShell) :
```powershell
.venv\Scripts\Activate.ps1
```
(Si PowerShell refuse : `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`)

macOS / Linux :
```bash
source .venv/bin/activate
```
Tu dois voir `(.venv)` au début de la ligne.

## 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Lancer le programme

```bash
python agent.py
```
Tape `quit` pour quitter.

## 5. Questions à essayer

| Question | Outils que le LLM devrait choisir |
|---|---|
| Quel est le budget de Banque Horizon en dollars ? | `infos_client` puis `convertir_euros` |
| Quelle date sommes-nous ? | `date_du_jour` |
| Dans quelle ville est Energia Nord ? | `infos_client` |
| Convertis 1000 euros en francs CFA | `convertir_euros` (devise XOF) |
| Bonjour, qui es-tu ? | Aucun outil : il répond directement |

Les lignes `[outil]` et `[résultat]` montrent ce que le LLM a décidé d'appeler.

## Les 3 outils

| Outil | Rôle |
|---|---|
| `infos_client(nom)` | Fiche d'un client fictif : secteur, ville, projet, budget |
| `convertir_euros(montant, devise)` | Conversion vers USD, GBP, XOF, MAD (taux figés pour l'exercice) |
| `date_du_jour()` | La date du jour, que le LLM ne connaît pas |

## 6. TP : l'interface web (type ChatGPT)

```bash
python app.py
```
Puis ouvre **http://127.0.0.1:5000** dans ton navigateur. Pour arrêter le serveur : `Ctrl+C` dans le terminal.

| Fichier | Rôle |
|---|---|
| `app.py` | Le serveur web Flask : affiche la page et reçoit les questions sur `/api/chat` |
| `templates/index.html` | La page de chat : HTML (structure), CSS (style), JavaScript (comportement) |
| `agent.py` | L'agent, réutilisé par `app.py` grâce à la fonction `executer_agent` |

Le guide **Guide_Projet2_Agent_et_Interface_Web.pdf** détaille chaque étape.

## Erreurs fréquentes

| Message | Cause |
|---|---|
| `KeyError: 'CHAT_DEPLOYMENT'` | `.env` absent ou variable non remplie |
| `ModuleNotFoundError: No module named 'dotenv'` | `.venv` non activé ou étape 3 oubliée |
| `401` / `404 DeploymentNotFound` | Clé ou nom de déploiement incorrect |
| `ModuleNotFoundError: No module named 'flask'` | Relancer `pip install -r requirements.txt` |
| `Address already in use` (port 5000) | Un autre serveur tourne : `app.run(port=5001)` |
| La page affiche « Impossible de joindre le serveur » | `python app.py` n'est pas lancé ou a planté (lire le terminal) |
