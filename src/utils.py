import requests
import time
import random
import json
from bs4 import BeautifulSoup

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
    "Accept-Encoding": "gzip, deflate, br, zstd", 
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",  
    "Priority": "u=0, i", 
    "Sec-Ch-Ua": "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"", 
    "Sec-Ch-Ua-Mobile": "?0", 
    "Sec-Ch-Ua-Platform": "\"Windows\"", 
    "Sec-Fetch-Dest": "document", 
    "Sec-Fetch-Mode": "navigate", 
    "Sec-Fetch-Site": "cross-site", 
    "Sec-Fetch-User": "?1", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
}

def scrap_animes(nr_pages=10):
    """Scrape anime titles and links from MAL top anime by popularity"""
    all_animes = []

    for page in range(nr_pages):
        limit = page * 50
        MAL_endpoint = f"https://myanimelist.net/topanime.php?type=bypopularity&limit={limit}"
        print(f"Scraping page {page + 1}/{nr_pages}...")

        try:
            response = requests.get(MAL_endpoint, headers=headers)
            response.raise_for_status()

        except Exception as e:
            print(f"Error on page {page + 1}: {e}")
        
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            h3_titles = soup.select("h3.anime_ranking_h3 > a")
            for title_tag in h3_titles:
                name = title_tag.getText()
                link = title_tag["href"]
                anime_data = scrap_anime_data(name, link)
                if anime_data:
                    all_animes.append(anime_data)
        
        if page < nr_pages - 1:
            time.sleep(random.uniform(1, 3))

    return all_animes

def scrap_anime_data(name, link):
    time.sleep(1)
    print(f"Scraping {name}...")

    try:
        response = requests.get(link, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.select_one("h1.title-name strong").getText()
        score = soup.select_one("div.score-label").getText()
        genres = soup.find_all(name="span", itemprop="genre")
        episodes_div = soup.find(name="span", class_="dark_text", string="Episodes:")
        episodes_text = episodes_div.parent.text.strip()
        episodes = episodes_text.replace("Episodes:\n  ", "")
        synopsis = soup.find(name="p", itemprop="description").getText()[:-27]
        popularity = soup.select_one("span.popularity strong").getText()[1:]
        members_string = soup.select_one("span.members strong").getText()
        members = members_string.replace(",", "")
        studios_div = soup.find(name="span", class_="dark_text", string="Studios:")
        studios_a = studios_div.parent.find_all('a')
        studios = [studio.getText() for studio in studios_a]
        year_div = soup.find(name="span", class_="dark_text", string="Premiered:")
        year = year_div.parent.find("a").getText().split()[1]

        anime_data = {
            "title": title,
            "score": float(score),
            "genres": [genre.text for genre in genres],
            "episodes": int(episodes),
            "synopsis": synopsis,
            "popularity": int(popularity),
            "members": int(members),
            "studios": studios,
            "year": year,
        }

        return anime_data

    except Exception as e:
           print(f"Error: {e}")
           return None