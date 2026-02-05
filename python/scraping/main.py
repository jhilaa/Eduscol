from scraping import utils
import os
import re
from urllib.parse import urlsplit, urljoin

# accepte:
#  - /document/299/download
#  - /4089/pratique-enseignante
#  - /388/enseigner-les-fondamentaux
PATH_RE = re.compile(r"^/(?:document/)?\d+/[A-Za-z0-9][A-Za-z0-9\-_/]*$")

BASE_URL = "https://eduscol.education.fr"

# Tu mets ici tes URLs SANS domaine
PATHS_SRC = [
"/388/enseigner-les-fondamentaux",
"/100/mener-un-projet-avec-ses-eleves",
"/103/enseigner-avec-le-numerique",
"/75/se-former",
"/98/innover-et-experimenter"
]

def clean_href(href: str) -> str | None:
    if not href:
        return None

    # Ignore mailto:, javascript:, tel:, etc.
    if re.match(r"^(mailto:|tel:|javascript:)", href, flags=re.I):
        return None

    # On enlève ?query et #fragment, on garde uniquement le path
    parts = urlsplit(href)
    path = parts.path

    # Normaliser: retirer un éventuel slash final
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    # Filtre format attendu
    return path if PATH_RE.match(path) else None

def extract_links_data(soup, source_url: str) -> list[dict]:
    """
    Extrait les liens par article, en évitant les articles imbriqués.
    Retourne une liste de dicts: {source, url, text, ...name_attrs}
    """
    results: list[dict] = []
    seen_local = set()

    for article in soup.find_all("article"):
        for a in article.find_all("a", href=True):

            # évite les <a> venant d'articles imbriqués
            if a.find_parent("article") is not article:
                continue

            path = clean_href(a["href"])
            if not path or path in seen_local:
                continue
            seen_local.add(path)

            # --- TEXTE ---
            text = a.get_text(strip=True) or None

            # --- ATTRIBUTS contenant "name" ---
            name_attrs = {
                attr: value
                for attr, value in a.attrs.items()
                if "name" in attr.lower()
            }
            if (source_url != path):
                results.append({
                    "source": source_url,
                    "url": path,
                    "text": text,
                    **name_attrs
            })

    return results

def main():
    urls_src = [urljoin(BASE_URL, p) for p in PATHS_SRC]

    seen_global = set()   # dédup globale sur le path extrait
    all_results: list[dict] = []
    all_results_single_row = []

    for url_src in urls_src:
        try:
            soup = utils.get_soup(url_src)
        except Exception as e:
            print(f"[ERREUR] {url_src} -> {e}")
            time.sleep(8)  # gros cooldown
            continue

        page_results = extract_links_data(soup, source_url=url_src)

        added = 0
        for row in page_results:
            key = row["url"]
            if key in seen_global:
                continue
            seen_global.add(key) 
            all_results.append(row)
            added += 1
            
            if (row["source"] != row["url"]):
                single_row = utils.strip_domain(row["source"])+";"+row["url"]+";"+row["text"]
                all_results_single_row.append(single_row)
                
        print(f"[OK] {url_src} -> {added} liens ajoutés (page={len(page_results)} avant dédup globale)")

    if all_results:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        utils.create_json_file(dir_name=script_dir, dataset_name="url", json_data=all_results)
        print(f"[EXPORT] {len(all_results)} liens uniques")
    else:
        print("[INFO] Aucun lien extrait")
        
    if all_results_single_row:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        utils.create_json_file(dir_name=script_dir, dataset_name="url_light", json_data=all_results_single_row)
        print(f"[EXPORT] {len(all_results_single_row)} liens uniques")
    else:
        print("[INFO] Aucun lien extrait")

if __name__ == "__main__":
    main()
