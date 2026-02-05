from scraping import utils
import os
import re
from collections import deque
from urllib.parse import urlsplit, urljoin

# accepte:
#  - /document/299/download
#  - /4089/pratique-enseignante
#  - /388/enseigner-les-fondamentaux
PATH_RE = re.compile(r"^/(?:document/)?\d+/[A-Za-z0-9][A-Za-z0-9\-_/]*$")

BASE_URL = "https://eduscol.education.fr"

# Pages de départ (sans domaine)

PATHS_SEED = [
    "/78/scolarite-de-l-eleve-et-diplomes"]
'''
"/793/vie-des-ecoles-et-des-etablissements",
"/4087/niveaux",
"/2347/disciplines",
"/4089/pratique-enseignante",
"/82/thematiques",
'''



def clean_href(href: str) -> str | None:
    if not href:
        return None

    if re.match(r"^(mailto:|tel:|javascript:)", href, flags=re.I):
        return None

    parts = urlsplit(href)
    path = parts.path

    if path != "/" and path.endswith("/"):
        path = path[:-1]

    return path if PATH_RE.match(path) else None

'''
def should_keep(path: str) -> bool:
    KEYWORDS = ["download", "math", "valuation", "programme", 
                 "attendus", "progression", "cycle4", "cycle 4", "collège", "lycée",
                 "3ème", "4ème", "5ème", "terminale", "seconde", "première", "générale", "problème"]
    p = path.lower()
    return ("download" in p) or ("math" in p) 
'''
def should_keep(path: str, text: str) -> bool:
    KEYWORDS = [
        "math", "valuation", "programme", "attendus", "progression",
        "cycle4", "cycle 4", "collège", "lycée", "3ème", "4ème", "5ème",
        "terminale", "seconde", "première", "générale", "problème", "download"
    ]

    FILTER = [
        "anglais", "espagnol", "français", "francais", "histoire", "géographie",
        "allemand", "italien", "section", "cycle 3", "cm1", "cm2", "langue", "biologie","physique", "chimie",
        "cycle 2", "cp", "primaire", "dictée", "art", "économie","econom"
    ]

    fields = [path.lower(), text.lower()]

    contains_keyword = any(k in field for field in fields for k in KEYWORDS)
    contains_filter  = any(f in field for field in fields for f in FILTER)

    return contains_keyword and not contains_filter


HIDDEN_CLASSES = {"hidden", "sr-only", "visually-hidden"}

def is_hidden(tag):
    if tag.has_attr("hidden"):
        return True
    if tag.has_attr("class") and any(c in HIDDEN_CLASSES for c in tag["class"]):
        return True
    return tag.find_parent(lambda t: t.has_attr("hidden") or
                                      (t.has_attr("class") and any(c in HIDDEN_CLASSES for c in t["class"])))

def extract_links_data(soup) -> list[dict]:
    results: list[dict] = []
    seen_local = set()

    for article in soup.find_all("article"):
        for a in article.find_all("a", href=True):
            if a.find_parent("article") is not article:
                continue
                
            # Exclure les éléments hidden ou dans un parent hidden 
            if is_hidden(a): continue

            path = clean_href(a["href"])
            if not path or path in seen_local:
                continue
            seen_local.add(path)

            text = a.get_text(strip=True) or None
            name_attrs = {k: v for k, v in a.attrs.items() if "name" in k.lower()}
            
            if should_keep(path, text):
                results.append({
                    "url": path,
                    "text": text,
                    **name_attrs
                })

    return results

def crawl_recursive(seeds: list[str], max_depth: int = 2, max_pages: int = 200) -> list[dict]:
    """
    Crawl récursif (implémenté en BFS) :
    - seeds: liste de paths de départ (sans domaine)
    - max_depth: profondeur de suivi des liens
    - max_pages: garde-fou anti-explosion
    """
    queue = deque()
    visited = set()        # URLs (complètes) déjà visitées
    seen_paths = set()     # paths extraits déjà rencontrés (dédup globale sur "url"=path)
    all_results: list[dict] = []

    domain = "root"
    depth = 0
    # init file
    for p in seeds: 
        full = urljoin(BASE_URL, p)
        queue.append((p, full, 0))

    while queue and len(visited) < max_pages:
        domain, page_url, depth = queue.popleft()

        if page_url in visited:
            continue
        visited.add(page_url)

        try:
            soup = utils.get_soup(page_url)
        except Exception as e:
            print(f"[ERREUR] {page_url} -> {e}")
            continue

        if soup :
            page_results = extract_links_data(soup)

        added = 0
        for row in page_results: 
            result = {}
            result["domain"] = domain
            result["source"] = page_url
            if "text" in row: 
                result["text"] = row["text"]
            if "data-ati-name" in row: 
                result["data-ati-name"] = row["data-ati-name"]
            result["url"] = row["url"]
            
            path = row["url"]
            # dédup globale sur le path
            if path in seen_paths:
                continue
            seen_paths.add(path)     
            if "download" in path :
                all_results.append(result)
                added += 1 

            # si on peut encore descendre en profondeur, on ajoute à la file
            if depth < max_depth:
                next_url = urljoin(BASE_URL, path)
                # garde-fou "même domaine"
                if urlsplit(next_url).netloc == urlsplit(BASE_URL).netloc:
                    queue.append((domain, next_url, depth + 1))

        print(f"[OK] depth={depth} {page_url} -> +{added} liens (page={len(page_results)})")

    print(f"[FIN] pages_visitées={len(visited)} liens_uniques={len(all_results)}")
    return all_results

def main():
    out = crawl_recursive(PATHS_SEED, max_depth=2, max_pages=200)

    if out:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        utils.create_json_file(dir_name=script_dir, dataset_name="url_recursive", json_data=out)
        print(f"[EXPORT] {len(out)} liens uniques")
    else:
        print("[INFO] Aucun lien extrait")

if __name__ == "__main__":
    main()
