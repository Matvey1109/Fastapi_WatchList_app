from src.config import API_KEY
import requests


def get_movie_from_api(movie_title, year):
    movie_title = movie_title.replace(" ", "%20")
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_title}&include_adult=false&language=en-US&page=1&year={year}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(url, headers=headers)
    return response.json()["results"][0]
