from bs4 import BeautifulSoup
import requests

# IMDB top 250 Movies
rank = 1
source = requests.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250').text

soup = BeautifulSoup(source, 'lxml')

table = soup.find('tbody', class_='lister-list')
for rowRaw in table.find_all('tr'):
    row = rowRaw.find('td', class_='titleColumn')
    title = row.a.text
    year = row.span.text.strip("()")
    ratingRaw = rowRaw.find('td', class_='ratingColumn imdbRating')
    rating = float(ratingRaw.text)
    user = ratingRaw.strong['title'].split(' ')[3]
    print(rank)
    print(title)
    print(year)
    print(rating)
    print(user)
    rank += 1




