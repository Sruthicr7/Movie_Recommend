import streamlit as st
from PIL import Image
import json
from Classifier import KNearestNeighbours
from bs4 import BeautifulSoup
import requests, io
import PIL.Image
from urllib.request import urlopen

# Define the correct file paths
TITLES_PATH = r"C:\Users\mouli padda\OneDrive\Desktop\python\DS\Movie_Recommender_App-master\Data\movie_titles.json"
DATA_PATH = r"C:\Users\mouli padda\OneDrive\Desktop\python\DS\Movie_Recommender_App-master\Data\movie_data.json"

# Load data from JSON files
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)
with open(TITLES_PATH, 'r', encoding='utf-8') as f:
    movie_titles = json.load(f)

hdr = {'User-Agent': 'Mozilla/5.0'}

def movie_poster_fetcher(imdb_link):
    url_data = requests.get(imdb_link, headers=hdr).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_dp = s_data.find("meta", property="og:image")
    if imdb_dp:
        movie_poster_link = imdb_dp.attrs['content']
        u = urlopen(movie_poster_link)
        raw_data = u.read()
        image = PIL.Image.open(io.BytesIO(raw_data))
        image = image.resize((158, 301))
        st.image(image, use_column_width=False)

def get_movie_info(imdb_link):
    url_data = requests.get(imdb_link, headers=hdr).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_content = s_data.find("meta", property="og:description")
    if not imdb_content:
        return "Unknown Director", "Unknown Cast", "No story available", "No ratings"
    
    movie_descr = imdb_content.attrs['content'].split('.')
    movie_director = movie_descr[0] if len(movie_descr) > 0 else "Unknown Director"
    movie_cast = f"Cast: {movie_descr[1].strip()}" if len(movie_descr) > 1 else "Unknown Cast"
    movie_story = f"Story: {movie_descr[2].strip()}." if len(movie_descr) > 2 else "No story available"
    rating = s_data.find("span", class_="sc-bde20123-1 iZlgcd")
    movie_rating = f'Total Rating count: {rating.text}' if rating else "No ratings"
    return movie_director, movie_cast, movie_story, movie_rating

def KNN_Movie_Recommender(test_point, k):
    target = [0 for _ in movie_titles]
    model = KNearestNeighbours(data, target, test_point, k=k)
    model.fit()
    return [[movie_titles[i][0], movie_titles[i][2], data[i][-1]] for i in model.indices]

st.set_page_config(page_title="Movie Recommender System")

def run():
    img1 = Image.open(r"C:\Users\mouli padda\OneDrive\Desktop\python\DS\Movie_Recommender_App-master\meta\logo.jpg").resize((250, 250))
    st.image(img1, use_column_width=False)
    st.title("Movie Recommender System")
    st.markdown("<h4 style='text-align: left; color: #d73b5c;'>* Data is based on IMDB 5000 Movie Dataset</h4>", unsafe_allow_html=True)

    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
    movies = [title[0] for title in movie_titles]
    category = ['--Select--', 'Movie based', 'Genre based']

    cat_op = st.selectbox('Select Recommendation Type', category)
    if cat_op == category[0]:
        st.warning('Please select Recommendation Type!!')
    elif cat_op == category[1]:
        select_movie = st.selectbox('Select movie:', ['--Select--'] + movies)
        if select_movie != '--Select--':
            no_of_reco = st.slider('Number of movies to recommend:', 5, 20, step=1)
            test_points = data[movies.index(select_movie)]
            table = KNN_Movie_Recommender(test_points, no_of_reco + 1)[1:]
            st.success('Recommended movies:')
            for c, (movie, link, ratings) in enumerate(table, 1):
                director, cast, story, total_rat = get_movie_info(link)
                st.markdown(f"({c}) [{movie}]({link})")
                st.markdown(director)
                st.markdown(cast)
                st.markdown(story)
                st.markdown(total_rat)
                st.markdown(f'IMDB Rating: {ratings}⭐')
                movie_poster_fetcher(link)
    elif cat_op == category[2]:
        sel_gen = st.multiselect('Select Genres:', genres)
        if sel_gen:
            imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
            no_of_reco = st.number_input('Number of movies:', 5, 20, step=1)
            test_point = [1 if genre in sel_gen else 0 for genre in genres] + [imdb_score]
            table = KNN_Movie_Recommender(test_point, no_of_reco)
            st.success('Recommended movies:')
            for c, (movie, link, ratings) in enumerate(table, 1):
                director, cast, story, total_rat = get_movie_info(link)
                st.markdown(f"({c}) [{movie}]({link})")
                st.markdown(director)
                st.markdown(cast)
                st.markdown(story)
                st.markdown(total_rat)
                st.markdown(f'IMDB Rating: {ratings}⭐')
                movie_poster_fetcher(link)

run()
