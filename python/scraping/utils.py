# scraping/utils.py
import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.7,en;q=0.6",
    "Connection": "keep-alive",
}

def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)

    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

SESSION = build_session()

def print_log(log: str, level: int = 0):
    print("   " * level + log)

def get_env(variable_name: str):
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=env_path)
    return os.getenv(variable_name)

def get_soup(url: str, timeout: int = 20) -> BeautifulSoup | None:
    """
    - Retourne BeautifulSoup si la ressource est du HTML
    - Retourne None si ce n'est pas du HTML (PDF, download, etc.)
    - Retry/SSL gérés via SESSION + backoff maison sur SSLError
    """

    # Politesse / anti-bot: petite pause aléatoire (UNE fois par page)
    time.sleep(random.uniform(0.6, 1.6))

    last_exc: Exception | None = None

    for attempt in range(1, 4):  # 3 tentatives "maison" en + des retries urllib3
        try:
            resp = SESSION.get(url, timeout=timeout, allow_redirects=True)
            resp.raise_for_status()

            content_type = (resp.headers.get("Content-Type") or "").lower()
            if "text/html" not in content_type:
                print(f"[SKIP NON HTML] {url} -> {content_type}")
                return None

            return BeautifulSoup(resp.text, "html.parser")

        except requests.exceptions.SSLError as e:
            last_exc = e
            time.sleep(4.0 * attempt + random.uniform(1, 2.6))

        except requests.exceptions.RequestException as e:
            last_exc = e
            break

    raise RuntimeError(f"get_soup failed for {url}: {last_exc}") from last_exc

def create_json_file(dir_name, dataset_name, json_data):
    subfolder = os.path.join(dir_name, "json")
    os.makedirs(subfolder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_name = os.path.join(subfolder, f"{dataset_name}_{timestamp}.json")

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"     [OK] Fichier généré : {file_name}")
    cleanup_json(subfolder, dataset_name, keep=1)

def cleanup_json(folder: str, begin_with: str, keep: int = 5):
    pattern = f"{begin_with}*.json"
    files = sorted(Path(folder).glob(pattern), key=lambda f: f.stat().st_mtime, reverse=True)

    for old_file in files[keep:]:
        old_file.unlink()
        print(f"[-] Supprimé : {old_file.name}")

def strip_domain(url: str) -> str:
    parts = urlsplit(url)
    return parts.path
