from bs4 import BeautifulSoup
import requests
import sqlite3
from sqlite3 import Error as DBError

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except DBError as e:
        print(e)
    return conn

def scrape_imdb_top250():
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
        no_of_users = int(no_of_users.replace(',', ''))
        review_url = row.a['href']
        movie = (
            rank,
            title,
            year,
            rating,
            no_of_users,
            review_url
        )
        # print(movie)
        rank += 1
        movies.append(movie)

    return movies

""" for movie in movies:
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
    movie.update({'user_review_count': count}) """

def main():
    print("Starting Script")
    conn = create_connection('imdb_movies.db')
    c = conn.cursor()
    table_name = "movies"
    sql_table = f"""CREATE TABLE if not exists {table_name} (
        id INTEGER PRIMARY KEY,
        rank INTEGER NOT NULL,
        title text NOT NULL,
        year text NOT NULL,
        rating REAL,
        no_of_users INTEGER,
        review_url TEXT
        );"""
    c.execute(sql_table)
    print(sql_table)
    print(c.rowcount)
    if c.rowcount == 250:
        print("Data Already Exists")
    else:
        movies = scrape_imdb_top250()
        insert_query = "INSERT INTO movies (rank, title, year, rating,no_of_users, review_url) VALUES(?, ?, ?, ?, ?, ?);"
        c.executemany(insert_query, movies)
        print('We have inserted', c.rowcount, 'records to the table.')

        #commit the changes to db
        conn.commit()
        #close the connection
        conn.close()

if __name__ == '__main__':
    main()

