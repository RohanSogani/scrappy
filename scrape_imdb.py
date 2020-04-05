from bs4 import BeautifulSoup
import requests
import sqlite3
from sqlite3 import Error as DBError
from random import randint
from time import sleep

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
    """ Scrapes imdb top 250 page to find rank, title, year, rating, no of users rated, url for user reviews
    """
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
        rank += 1
        movies.append(movie)

    return movies

def scrape_user_reviews(movies):
    """ Scrapes the user review page for all movies and collects reviews from the top reviewers. The data from this can be further used for sentiment analysis and other data analysis.
    :param movies: list of movies that contains the url to reviews
    :return user_reviews: list of user reviews for each movie
    """
    user_reviews = []
    for movie in movies:
        review_count = 0
        review_movie_rank = movie[1]
        review_movie = movie[2]
        review_url = movie[6]
        # form the proper url
        review_url = f"https://www.imdb.com/{review_url}reviews?sort=reviewVolume&dir=desc&ratingFilter=0"
        # sleep for random time to avoid IP Block
        # sleep(randint(1, 5))
        response = requests.get(review_url).text
        soup = BeautifulSoup(response, 'lxml')

        for review_container in soup.find_all('div', class_='imdb-user-review'):
            review_meta = review_container.find('div', class_='display-name-date')
            review_title = review_container.a.text.strip('\n')
            review_date = review_container.find('span', class_='review-date').text
            reviewer_rating = review_container.find('div', class_='ipl-ratings-bar')
            if reviewer_rating == None:
                reviewer_rating = ''
            else:
                reviewer_rating = reviewer_rating.text.strip('\n')
            reviewer =  review_meta.a.text
            review_content = review_container.find('div', class_='content').div.text
            review = (
                review_count,
                review_movie,
                review_movie_rank,
                review_title,
                reviewer_rating,
                reviewer,
                review_date,
                review_content
            )
            review_count += 1
            print(review_movie, review_count)
            user_reviews.append(review)
    return user_reviews

def create_movies_db(table_name, table_create_query, insert_query):
    pass

def main():
    print("Starting Script")
    conn = create_connection('imdb_movies.db')
    c = conn.cursor()
    table_name_movie = "movies"
    sql_table_movie = f"""CREATE TABLE if not exists {table_name_movie} (
        id INTEGER PRIMARY KEY,
        rank INTEGER NOT NULL,
        title text NOT NULL,
        year text NOT NULL,
        rating REAL,
        no_of_users INTEGER,
        review_url TEXT
        );"""
    c.execute(sql_table_movie)
    row_count = c.execute(f'SELECT COUNT(*) FROM {table_name_movie}')
    row_count = int(str(next(row_count)).split(",")[0].strip('('))
    movies =[]
    if row_count == 250:
        print("Data For Movies Already Exists")
        c.execute(f"SELECT * FROM {table_name_movie}")
        movies = c.fetchall()
    else:
        movies = scrape_imdb_top250()
        insert_movies_query = "INSERT INTO movies (rank, title, year, rating,no_of_users, review_url) VALUES(?, ?, ?, ?, ?, ?);"
        c.executemany(insert_movies_query, movies)
        print('We have inserted', c.rowcount, 'records to the table.')

    table_name_reviews = "reviews"
    sql_table_reviews = f"""CREATE TABLE if not exists {table_name_reviews} (
        id INTEGER PRIMARY KEY,
        review_count INTEGER,
        review_movie TEXT NOT NULL,
        review_movie_rank INTEGER NOT NULL,
        review_title TEXT NOT NULL,
        reviewer_rating TEXT NOT NULL,
        reviewer TEXT NOT NULL,
        review_date TEXT,
        review_content TEXT
        );"""
    c.execute(sql_table_reviews)
    c.execute(sql_table_reviews)
    row_count = c.execute(f'SELECT COUNT(*) FROM {table_name_reviews}')
    row_count = int(str(next(row_count)).split(",")[0].strip('('))
    user_reviews =[]
    if row_count == 6249:
        print("Data For Reviews Already Exists")
        c.execute(f"SELECT * FROM {table_name_reviews}")
        user_reviews = c.fetchall()
    else:
        user_reviews = scrape_user_reviews(movies)
        insert_reviews_query = "INSERT INTO reviews (review_count, review_movie, review_movie_rank, review_title, reviewer_rating, reviewer, review_date, review_content) VALUES(?, ?, ?, ?, ?, ?, ?, ?);"
        c.executemany(insert_reviews_query, user_reviews)
        print('We have inserted', c.rowcount, 'records to the table.')

    #commit the changes to db
    conn.commit()
    #close the connection
    conn.close()

if __name__ == '__main__':
    main()