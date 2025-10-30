import requests
import time
import random
import json
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

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
                link = title_tag["href"]
                anime_data = scrap_anime_data(link)
                if anime_data:
                    all_animes.append(anime_data)
        
        if page < nr_pages - 1:
            time.sleep(random.uniform(1, 3))

    return all_animes

def scrap_anime_data(link):
    time.sleep(1)

    try:
        response = requests.get(link, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            title = soup.select_one("p.title-english").getText()
        except:
            title = soup.select_one("h1.title-name strong").getText()
        
        print(f"Scraping {title}...")
        
        score_element = soup.select_one("div.score-label")
        score = score_element.getText() if score_element else None
        
        genres = soup.find_all(name="span", itemprop="genre")
        
        episodes_div = soup.find(name="span", class_="dark_text", string="Episodes:")
        if episodes_div:
            episodes_text = episodes_div.parent.text.strip()
            episodes = episodes_text.replace("Episodes:\n  ", "").strip()
        else:
            episodes = None
        
        synopsis_element = soup.find(name="p", itemprop="description")
        synopsis = synopsis_element.getText()[:-27] if synopsis_element else ""
        
        popularity_element = soup.select_one("span.popularity strong")
        popularity = popularity_element.getText()[1:] if popularity_element else None
        
        members_element = soup.select_one("span.members strong")
        members_string = members_element.getText() if members_element else "0"
        members = members_string.replace(",", "")
        
        studios_div = soup.find(name="span", class_="dark_text", string="Studios:")
        if studios_div:
            studios_a = studios_div.parent.find_all('a')
            studios = [studio.getText() for studio in studios_a]
        else:
            studios = []
        
        year_div = soup.find(name="span", class_="dark_text", string="Premiered:")
        if year_div:
            year_link = year_div.parent.find("a")
            year = year_link.getText().split()[1] if year_link else None
        else:
            year = None

        anime_data = {
            "title": title,
            "score": float(score) if score else None,
            "genres": [genre.text for genre in genres],
            "episodes": int(episodes) if episodes and episodes.isdigit() else None,
            "synopsis": synopsis,
            "popularity": int(popularity) if popularity else None,
            "members": int(members) if members else None,
            "studios": studios,
            "year": year,
        }
        return anime_data

    except Exception as e:
        print(f"Error: {e}")
        return None

def store_data(animes, file_name="anime_dataset"):
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(animes)

    csv_path = data_dir / f"{file_name}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Saved {len(animes)} animes into {csv_path}")

    json_path = data_dir / f"{file_name}.json"
    with open(json_path, "w", encoding='utf-8') as file:
        json.dump(animes, file, indent=4, ensure_ascii=False)
    print(f"Saved {len(animes)} animes into {json_path}")

    print(f"\n{'='*50}")
    print("Dataset Summary")
    print(f"Total animes: {len(animes)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\n{'='*50}")

    return csv_path, json_path