from flask import Flask
from flask import render_template
from flask import Response
import sqlite3
import random
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


app = Flask(__name__)


@app.route("/")
def cv_index():
    cvs = get_cv()
    res = ""
    for i, cv in enumerate(cvs):
        res += f"<h1>{i + 1})</h1>"
        res += f"<p>Желаемая зарплата: {cv['salary']}.</p>"
        res += f"<p>Образование: {cv['educationType']}.</p>"

    return res


@app.route("/dashboard")
def dashboard():
    con = sqlite3.connect('works.sqlite')
    res = con.execute('SELECT SUBSTR(dateModify, 1, 4), COUNT(*) FROM works WHERE dateModify NOT NULL GROUP BY '
                      'SUBSTR(dateModify, 1, 4)').fetchall()
    con.close()
    return render_template('d3.html',
                           cvs=get_cv(),
                           labels=[row[0] for row in res],
                           data=[row[1] for row in res]
                           )


@app.route("/statistic")
def statistic():
    job_titles = get_list_field('jobTitle')
    qualifications = get_list_field('qualification')
    res = ""
    count = get_match_count(job_titles, qualifications)
    res += f"<p>У {count[1] - count[0]} человек  из {count[1]} не совпадают профессия и должность.</p>"
    res += "<p>Топ 5 квалификаций менеджеров:<br>"
    for item in get_top('jobTitle', 'qualification', 'менеджер'):
        res += f"{item[0]} {item[1]}</br>"
    res += "</p><p>Топ 5 должностей инженеров:<br>"
    for item in get_top('qualification', 'jobTitle', 'инженер'):
        res += f"{item[0]} {item[1]}</br>"
    res += "</p>"
    return res


def get_list_field(field):
    con = sqlite3.connect('works.sqlite')
    res = list(con.execute(f'select {field} from works'))
    con.close()
    return res


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
    res = list(con.execute('select * from works limit 20'))
    con.close()
    return res


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig


def get_match_count(first_list, second_list):
    return len(list((filter(lambda x: contains(x[0], x[1]) or contains(x[1], x[0]), zip(first_list, second_list))))),\
           len(list(zip(first_list, second_list)))


def contains(sub_text, text):
    words = str(sub_text).lower().replace('-', ' ').split()
    for word in words:
        if word in str(text).lower():
            return True
    return False


def get_top(search_field, return_field, value):
    con = sqlite3.connect('works.sqlite')
    cur = con.cursor()
    cur.execute(f"SELECT LOWER({return_field}), count(*) AS 'count' FROM works "
                f"WHERE {return_field} IS NOT NULL AND "
                f"(LOWER({search_field}) like '%{value}%')"
                f"GROUP BY LOWER({return_field}) "
                f"ORDER BY count DESC LIMIT 5")
    return cur.fetchall()


app.run()
