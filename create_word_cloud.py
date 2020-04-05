import sqlite3
from sqlite3 import Error as DBError
from scrape_imdb import create_connection
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd

conn = create_connection('imdb_movies.db')
c = conn.cursor()
table_name_reviews = "reviews"

movie_name = input("Enter a movie to get a word cloud --> ")

reviews = c.execute(f'SELECT review_content FROM {table_name_reviews} WHERE review_movie = "{movie_name}"')

reviews = reviews.fetchall()
# print(review[0])

stop_words = set(STOPWORDS)
stop_words.add('film')
stop_words.add('movie')
stop_words.add('films')
stop_words.add('movies')
stop_words.add('actor')
stop_words.add('actors')
stop_words.add('imdb')
stop_words.add('well')
stop_words.add('will')
stop_words.add('didn')
ignore_movie = movie_name.split(' ')
for w in ignore_movie:
    stop_words.add(w)
review_words = ' '
print(stop_words)
for r in reviews:
    r = str(r)
    tokens = r.split()
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
    for words in tokens:
        review_words = review_words + words + ' '

wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stop_words,
                min_font_size = 10).generate(review_words)


plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)
plt.show()

conn.commit()
conn.close()
