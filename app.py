import streamlit as st
import pickle
import re
import requests

with open('songs.pkl', 'rb') as f:
    new_df = pickle.load(f)

with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)


def clean_name(name):
    name = re.sub(r'\(.*?\)', '', name)   # (From "Brahmastra") jaisa bracket wala hissa hatao
    name = re.sub(r'\s-\s.*$', '', name)  # " - Lofi Flip" jaisa dash ke baad wala hissa hatao
    return name.strip().lower()


def recommend(song_name):
    song_index = new_df.index[new_df['track_name'] == song_name].tolist()
    if song_index == []:
        return 'Song Not Available'

    scores = similarity[song_index[0]]
    sorted_value = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    seen = {clean_name(song_name)}
    recommended_songs = []
    for idx, score in sorted_value:
        base = clean_name(new_df.iloc[idx]['track_name'])
        if base in seen:
            continue
        seen.add(base)
        recommended_songs.append(new_df.iloc[idx][['track_name', 'artists', 'track_id']].to_dict())
        if len(recommended_songs) == 5:
            break
    return recommended_songs


@st.cache_data(show_spinner=False)
def get_preview(song_name, artist):
    response = requests.get(
        'https://itunes.apple.com/search',
        params={'term': f'{song_name} {artist}', 'entity': 'song', 'limit': 1}
    )

    data = response.json()
    if data['results'] == []:
        return None, None

    first = data['results'][0]
    audio_link = first.get('previewUrl')
    image_link = first.get('artworkUrl100')

    if image_link:
        image_link = image_link.replace('100x100', '300x300')

    return audio_link, image_link


st.title('Song Recommendation System')
selected_song = st.selectbox(
    "Type or select a song from the dropdown",
    new_df['track_name'].values)


if st.button('Show Recommendation'):
    with st.spinner('wait... 🔍'):
        result = recommend(selected_song)
    cols = st.columns(5)
    for col, song in zip(cols, result):
        with col:
            st.caption(song['track_name'])
            st.write(song['artists'])
            first_artist = song['artists'].split(';')[0]
            audio, image = get_preview(song['track_name'], first_artist)
            if image:
                st.image(image)
            if audio:
                st.audio(audio, end_time=30)