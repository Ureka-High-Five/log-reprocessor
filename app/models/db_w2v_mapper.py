_genre_mapping = {
    "공포": "Horror",
    "액션": "Action",
    "스릴러": "Thriller",
    "미스터리": "Mystery",
    "가족": "Family",
    "코미디": "Comedy",
    "애니메이션": "Animation",
    "SF": "SF",
    "다큐멘터리": "Documentary",
    "판타지": "Fantasy",
    "드라마": "Drama",
    "모험": "Adventure",
    "로맨스": "Romance",
    "범죄": "Crime",
    "역사": "History",
    "음악": "Music",
    "전쟁": "War",
    "Action & Adventure": "Adventure",
    "Sci-Fi & Fantasy": "Fantasy",
    "Kids": "Children",
    "War & Politics": "War",
    "Talk": "Talkshow",
}


def translate_genre(korean_genre: str) -> str:
    return _genre_mapping.get(korean_genre, korean_genre)
