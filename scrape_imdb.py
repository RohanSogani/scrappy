from bs4 import BeautifulSoup
import requests

# IMDB top 250 Movies
source = requests.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250').text

soup = BeautifulSoup(source, 'lxml')

table = soup.find('tbody', class_='lister-list')

rank = 1
movies = []
for rowRaw in table.find_all('tr'):
    row = rowRaw.find('td', class_='titleColumn')
    title = row.a.text
    year = row.span.text.strip("()")
    ratingRaw = rowRaw.find('td', class_='ratingColumn imdbRating')
    rating = float(ratingRaw.text)
    no_of_users = ratingRaw.strong['title'].split(' ')[3]
    top_user_reviews_link = f"https://www.imdb.com/{row.a['href']}reviews?sort=reviewVolume&dir=desc&ratingFilter=0"
    movie = {
        "rank": {rank},
        "title": {title},
        "year": {year},
        "rating": {rating},
        "no_of_users": {no_of_users},
        "review_links": {top_user_reviews_link}
    }
    # print(movie)
    rank += 1
    movies.append(movie)

print(movies)




