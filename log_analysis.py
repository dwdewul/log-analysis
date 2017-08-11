import psycopg2
from datetime import datetime

DB_NAME = "news"

################################################################################
#####       Completed functions
################################################################################

# This method returns the top 3 articles ordered by number of views
def get_top_articles():
    db = psycopg2.connect(database=DB_NAME)
    c = db.cursor()
    c.execute("""SELECT title, count(path) FROM articles, log
                WHERE status LIKE '200%'
                AND  CONCAT('/article/', articles.slug) = log.path
                GROUP BY title
                ORDER BY count(path) ASC
                LIMIT 3
                """)
    return c.fetchall()
    db.close()

# This method returns all authors ordered by the sum of their article views
def get_authors_views():
    db = psycopg2.connect(database=DB_NAME)
    c = db.cursor()
    c.execute("""SELECT name, count(log.id)
                    FROM authors, articles, log
                    WHERE articles.author = authors.id and
                    log.status LIKE '200%'
                    GROUP BY name
                    ORDER BY count(log.id) DESC""")
    return c.fetchall()
    db.close()

# This method returns the total article view count by date
def get_articles_count():
    db = psycopg2.connect(database=DB_NAME)
    c = db.cursor()
    c.execute("""SELECT count(id), DATE(time) FROM log
                WHERE status LIKE '200%'
                GROUP BY DATE(time)
                ORDER BY DATE(time)
                """)
    return c.fetchall()
    db.close()

# This metho returns all of the article views that had errors by date
def get_errors_count():
    db = psycopg2.connect(database=DB_NAME)
    c = db.cursor()
    c.execute("""SELECT count(id), DATE(time) FROM log
                WHERE status LIKE '404%'
                GROUP BY DATE(time)
                ORDER BY DATE(time)
                """)
    return c.fetchall()
    db.close()

# This function combines the get_errors_count list and the get_articles_count
# functions and does the data analysis on them, then prints where the total
# errors were higher than 1% for a given date
def error_data(list1, list2):
    q = zip(list1, list2)
    for i in q:
        error_percent = (float(i[0][0]) / i[1][0]) * 100
        if error_percent > 1:
            date = datetime.strptime(str(i[0][1]), "%Y-%m-%d").strftime("%d %b, %Y")
            error_formatted = str(error_percent)[:3]
            return("{} -- {}% errors".format(date, error_formatted))


################################################################################
#####       Testing area
################################################################################

if __name__ == '__main__':
    for article in get_top_articles():
        print("Article: {} -- Hits: {:,d}".format(article[0], article[1]))
    print("--------------------------------------------------- \n")
    for q in get_authors_views():
        print("Author: {} -- Views: {:,d}".format(q[0], q[1]))
    print("--------------------------------------------------- \n")
    print(error_data(get_errors_count(), get_articles_count()))
    print("--------------------------------------------------- \n")
