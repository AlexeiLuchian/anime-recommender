"""
Anime Recommendation System
Content-based filtering using cosine similarity
"""

import pandas as pd
import numpy as np


def get_recommendations(anime_title, titles, similarity_df, n_recommendations=10):
    """ Get anime recommendations based on similarity """
    
    try:
        anime_idx = titles[titles['title'] == anime_title].index[0]
    except IndexError:
        print(f"❌ Error: '{anime_title}' not found in database!")
        print(f"\nTip: Try searching for it first using search_anime()")
        return None
    
    similarity_scores = similarity_df.iloc[anime_idx]
    similarity_scores = similarity_scores.sort_values(ascending=False)
    
    # Get top N (excluding the anime itself, which is always #1)
    top_similar = similarity_scores.iloc[1:n_recommendations+1]
    
    recommendations = pd.DataFrame({
        'Rank': range(1, len(top_similar) + 1),
        'Anime': top_similar.index,
        'Similarity Score': top_similar.values,
        'Match %': (top_similar.values * 100).round(1)
    })
    
    return recommendations

print("Recommender function created!")

def search_anime(titles, keyword):
    """ Search for anime titles containing a keyword """
    keyword = keyword.lower()
    matches = titles[titles['title'].str.lower().str.contains(keyword)]
    
    if len(matches) == 0:
        print(f"❌ No anime found containing '{keyword}'")
        return None
    
    print(f"Found {len(matches)} anime matching '{keyword}':")
    for idx, row in matches.iterrows():
        print(f"  -> {row['title']}")
    
    return matches['title'].tolist()

print("Search function created!")