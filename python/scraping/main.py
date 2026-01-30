from scraping import utils
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import urljoin

# --- Orchestration ---
def main():
        # URLs
    # url_src = "https://eduscol.education.fr/4087/niveaux"
    url_src = "https://eduscol.education.fr/90/j-enseigne-au-cycle-4"
    soup = utils.get_soup(url_src)
    
    print(url_src)
    h1 = soup.select_one('h1.page__title')
    print(url_src)
    h2_block_titles = soup.select('h2.block-title')
    if (len(h2_block_titles) > 0):
        for h2_block_title in h2_block_titles :
            print (h2_block_title.get_text(strip=True))
            h2_block_title_parent = h2_block_title.find_parent()
            articles = h2_block_title_parent.select("div[role=""article""]")
            
            if (len(articles) > 0):
                for  article in articles:
                    item_link = article.select_one('.item-link')  
                    href = item_link.get("href") if item_link  else None
                    
                    item_image = item_link.select_one('.item-image') if item_link else None
                    img = item_image.select_one("img") if item_image else None
                    img_src = img.get("src") if img else None
                    
                    item_content = item_link.select_one('.item-content') if item_link else None
                    item_content_block_title = item_content.select_one(".block-title")
                    item_content_block_description = item_content.select_one(".block-description")
                    print ("--------------")
                    print (href)
                    print (img_src)
                    print (item_content_block_title.get_text(strip=True) if item_content_block_title else None)
                    print (item_content_block_description.get_text(strip=True) if item_content_block_description else None)
                    print ("--------------")
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
                  

if __name__ == "__main__":
    main()
    