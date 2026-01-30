import requests
import json
import os
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime


# Ecrit un log avec le niveau d'indentation demandé
def print_log (log: str, level: int = 0):
    print ("   " * level + log)
    
# Renvoie la valeur de la variable d'environnement demandée, à partir du .env situé au même niveau que ce script
def get_env (variable_name: str):
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=env_path)
    return os.getenv(variable_name)

# Récupère les données brutes d'une page web
def get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")
        
# Ecrit les données json dans un fichier
def create_json_file (dir_name, dataset_name, json_data):
    subfolder = os.path.join(dir_name, "json")
    os.makedirs(subfolder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    # Chemin complet du fichier
    file_name = os.path.join(subfolder, f"{dataset_name}_{timestamp}.json")
    
    # Écriture du fichier JSON en UTF-8
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"     [OK] Fichier généré : {file_name}")
    # On ne garde que les 2 derniers fichiers
    cleanup_json (subfolder, dataset_name, keep=1)
   
        
# ménage dans le répertoire cible
def cleanup_json(folder: str, begin_with: str, keep: int = 5):
    # Liste tous les fichiers JSON qui commencent par begin_with
    pattern = f"{begin_with}*.json"
    files = sorted(Path(folder).glob(pattern),
                   key=lambda f: f.stat().st_mtime,
                   reverse=True)
    
    # Supprime les plus anciens au-delà du quota
    for old_file in files[keep:]:
        old_file.unlink()
        print(f"[-] Supprimé : {old_file.name}")
        


def post_json(url: str, payload: dict | list, headers: dict | None = None, timeout: int = 30) -> requests.Response:
    """
    Envoie un JSON vers un endpoint via POST.
    Args:
        url (str): URL complète de l'endpoint ORDS/APEX.
        payload (dict | list): Données à envoyer (dict ou liste de dicts).
        headers (dict | None): Headers HTTP optionnels. 
                               Par défaut : {"Content-Type": "application/json"}
        timeout (int): Timeout en secondes (par défaut 30).

    Returns:
        requests.Response: Objet réponse HTTP (status_code, text, etc.)
    """
    if headers is None:
        headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()  # lève une exception si code != 200
        print(f"[OK] POST réussi : {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[X] Erreur lors du POST vers APEX : {e}")
        raise
    return response

        
