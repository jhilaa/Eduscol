from bs4 import BeautifulSoup
import requests
from datetime import datetime
from urllib.parse import urljoin
#
from scraping import utils


def get_competitions (): 
    # URLs
    # url_src = "https://eduscol.education.fr/4087/niveaux"
    url_src = "https://eduscol.education.fr/90/j-enseigne-au-cycle-4"
    soup = utils.get_soup(url_src)
    
    print(url_src)
    h1 = soup.select_one('h1.page__title')
    print(url_src)
    h2 = soup.select('h2.block-title')
    if (len(h2) > 0):
        print (h2.get_text(strip=True))
    '''
    competitions_list = []
    if soup :
        competitions_url = soup.select('a[href^="/classements/"][href*=".html?sx="]')
        if (len(competitions_url) > 0):
            for a in competitions_url:
                href = a.get("href")
                menu_label = a.get_text(strip=True)
                
                competition_url = urljoin(utils.get_env("domain"), href)
                competition_soup = utils.get_soup(competition_url)
                competitions_list.append({"url": href, "menu_label": menu_label, "soup": competition_soup})
    
    return (competitions_list)
    '''
                  
# --- Orchestration ---
if __name__ == "__main__":
    main()

