from flask import Flask
from datetime import datetime
import sqlite3

app = Flask(__name__)


@app.route("/")
def hello_world():
    return str(get_cv())


def dict_factory(cursor, row):
    # обертка для преобразования
    # полученной строки. (взята из документации)
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_cv():
    con = sqlite3.connect('works.sqlite')
    con.row_factory = dict_factory
    res = list(con.execute('select * from works limit 3'))
    con.close()
    return res


app.run()