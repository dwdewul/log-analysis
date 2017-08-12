#! /usr/bin/env python3
import psycopg2
from datetime import datetime

DB_NAME = "news"

################################################################################
# Completed functions
################################################################################

# Connection method


def connect(database_name="news"):
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("Could not connect")

# This method returns the top 3 articles ordered by number of views


def get_top_articles():
    db, c = connect()
    c.execute("""SELECT title, count(path) FROM articles, log
                WHERE status LIKE '200%'
                AND  CONCAT('/article/', articles.slug) = log.path
                GROUP BY title
                ORDER BY count(path) DESC
                LIMIT 3
                """)
    return c.fetchall()
    db.close()

# This method returns all authors ordered by the sum of their article views


def get_authors_views():
    db, c = connect()
    c.execute("""SELECT authors.name, COUNT(*)
                    FROM articles INNER JOIN authors ON articles.author = authors.id
                    INNER JOIN log ON CONCAT('/article/', articles.slug) = log.path
                    WHERE  log.status LIKE '200%'
                    GROUP BY authors.name
                    ORDER BY COUNT(log.path) DESC""")
    return c.fetchall()
    db.close()


# This method returns all of the article views that had errors by date and
# the total article counts
# I used this StackOverflow article to help me combine my SQL into one statement
# https://stackoverflow.com/questions/12789396/how-to-get-multiple-counts-with-one-sql-query
def get_errors_count():
    db, c = connect()
    c.execute("""SELECT DATE(time),
                SUM(CASE WHEN status LIKE '404%' THEN 1 ELSE 0 END) ErrCount,
                COUNT(id) AS TotCount
                FROM log
                GROUP BY DATE(time)
                ORDER BY DATE(time)
                """)
    return c.fetchall()
    db.close()

# This function combines the get_errors_count list and the get_articles_count
# functions and does the data analysis on them, then prints where the total
# errors were higher than 1% for a given date


def error_data(query_result):
    for i in query_result:
        # print(i[0])
        error_percent = (float(i[1]) / i[2]) * 100
        if error_percent > 1:
            date = datetime.strptime(
                str(i[0]), "%Y-%m-%d").strftime("%d %b, %Y")
            error_formatted = str(error_percent)[:4]
            return("{} -- {}% errors".format(date, error_formatted))


################################################################################
# Data Output
################################################################################

if __name__ == '__main__':
    for article in get_top_articles():
        print("Article: {} -- Hits: {:,d}".format(article[0], article[1]))
    print("--------------------------------------------------- \n")
    for q in get_authors_views():
        print("Author: {} -- Views: {:,d}".format(q[0], q[1]))
    print("--------------------------------------------------- \n")
    print(error_data(get_errors_count()))
    print("--------------------------------------------------- \n")
