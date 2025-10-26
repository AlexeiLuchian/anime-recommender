import streamlit as st
import pandas as pd
import pickle
import sys

sys.path.append('src')
from recommender import search_anime, get_recommendations

st.set_page_config(
    page_title="Anime Recommender",
    page_icon="🎌",
    layout="wide"
)

st.title("🎌 Anime Recommendation System")
st.markdown("""
Welcome! This AI-powered system recommends anime based on **80+ features** including:
- Genres, themes, and studios
- Episode count and release year
- Similarity to your favorite shows

**Just enter an anime you like and discover similar ones!**
""")

st.divider()

@st.cache_data
def load_data():
    with open('models/content_recommender.pkl', 'rb') as f:
        data = pickle.load(f)
    return data['titles'], data['similarity_df'], data['X_features']

with st.spinner('Loading anime database...'):
    titles, similarity_df, X_features = load_data()

st.success(f"✅ Loaded {len(titles)} anime in database!")

st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🔍 Search for Anime")
    
    # Search box
    search_query = st.text_input(
        "Enter anime name or keyword:",
        placeholder="e.g., Naruto, Attack, Death..."
    )
    
    # Search button
    if st.button("🔎 Search", type="primary"):
        if search_query:
            # Search for anime
            keyword = search_query.lower()
            matches = titles[titles['title'].str.lower().str.contains(keyword)]
            
            if len(matches) > 0:
                st.write(f"**Found {len(matches)} matches:**")
                for idx, row in matches.iterrows():
                    st.write(f"• {row['title']}")
            else:
                st.warning(f"No anime found with '{search_query}'")
        else:
            st.warning("Please enter a search term!")

with col2:
    st.subheader("🎯 Get Recommendations")
    
    # Dropdown to select anime
    selected_anime = st.selectbox(
        "Select an anime you like:",
        options=titles['title'].tolist(),
        index=0
    )
    
    # Number of recommendations slider
    num_recs = st.slider(
        "How many recommendations?",
        min_value=5,
        max_value=20,
        value=10
    )
    
    # Recommend button
    if st.button("🎬 Get Recommendations!", type="primary"):
        with st.spinner('Finding similar anime...'):
            # Get recommendations
            recs = get_recommendations(
                selected_anime, 
                titles, 
                similarity_df, 
                n_recommendations=num_recs
            )
            
            if recs is not None:
                st.success(f"Top {num_recs} recommendations for **{selected_anime}**:")
                
                # Display as a nice table
                st.dataframe(
                    recs,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show top 3 with explanations
                st.divider()
                st.subheader("💡 Why these recommendations?")
                
                for i in range(min(3, len(recs))):
                    recommended = recs['Anime'].iloc[i]
                    similarity = recs['Match %'].iloc[i]
                    
                    with st.expander(f"#{i+1} - {recommended} ({similarity}% match)"):
                        # Get shared features
                        source_idx = titles[titles['title'] == selected_anime].index[0]
                        rec_idx = titles[titles['title'] == recommended].index[0]
                        
                        source_features = X_features.iloc[source_idx]
                        rec_features = X_features.iloc[rec_idx]

                        shared_genres = []
                        shared_themes = []

                        for col in X_features.columns:
                            if source_features[col] == 1 and rec_features[col] == 1:
                                # Skip normalized/technical columns
                                if any(x in col for x in ['normalized', 'tier', 'score_cat', 'length', 'era']):
                                    continue
                                
                                # Separate genres from themes
                                if col.startswith('has_'):
                                    theme_name = col.replace('has_', '').replace('_', ' ').title()
                                    shared_themes.append(theme_name)
                                else:
                                    # It's a genre
                                    shared_genres.append(col)

                        if shared_genres:
                            st.write("**🎭 Shared Genres:**")
                            st.write(" • ".join(shared_genres))

                        if shared_themes:
                            st.write("**💡 Shared Themes:**")
                            st.write(" • ".join(shared_themes))

                        if not shared_genres and not shared_themes:
                            st.write("**Similar based on scores and popularity**")

# Footer
st.divider()
st.caption("Built with Streamlit | Data from MyAnimeList | ML-powered recommendations")