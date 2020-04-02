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
    top_user_reviews_link = row.a['href']
    movie = {
        "rank": rank,
        "title": title,
        "year": year,
        "rating": rating,
        "no_of_users": no_of_users,
        "review_url": top_user_reviews_link
    }
    # print(movie)
    rank += 1
    movies.append(movie)

# print(movies)

for movie in movies:
    user_reviews = []
    count = 0
    review_url = movie.get('review_url')
    # form the proper url
    review_url = f"https://www.imdb.com/{review_url}reviews?sort=reviewVolume&dir=desc&ratingFilter=0"
    # print(review_url)
    response = requests.get(review_url).text
    soup = BeautifulSoup(response, 'lxml')
    for review_container in soup.find_all('div', class_='imdb-user-review'):
        review_meta = review_container.find('div', class_='display-name-date')
        review_title = review_container.a.text.strip('\n')
        review_date = review_container.find('span', class_='review-date').text
        reviewer =  review_meta.a.text
        review_content = review_container.find('div', class_='content').div.text
        review = {
            "review_title": review_title,
            "reviewer": reviewer,
            "review_date": review_date,
            "review_content": review_content
        }
        count += 1
        user_reviews.append(review)
    movie.update({'user_reviews': user_reviews})
    movie.update({'user_review_count': count})



