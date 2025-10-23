from utils import scrap_animes, store_data

print("Start anime scraper...\n")
animes = scrap_animes()

print(f"\n{'='*50}")
print(f"Total anime scraped: {len(animes)}")
print(f"{'='*50}\n")

if animes:
    store_data(animes)
    print("Scraping complete! Data saved successfully.")
else:
    print("No anime data collected!")