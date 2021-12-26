from flask import Flask
from flask import render_template
from flask import Response
import sqlite3
import random
import io
import pandas

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
    result = con.execute('SELECT SUBSTR(dateModify, 1, 4), COUNT(*)'
                      ' FROM works'
                      ' WHERE dateModify NOT NULL'
                      ' GROUP BY SUBSTR(dateModify, 1, 4)').fetchall()
    con.close()
    return render_template('d2.html',
                           cvs=get_cv(),
                           labels=[row[0] for row in result],
                           data=[row[1] for row in result]
                           )


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

@app.route("/topJobs")
def topJobs():
    works = pandas.read_csv("works.csv").dropna()
    works = works.apply(lambda x: x.astype(str).str.lower())
    all_count = len(works)
    con = sqlite3.connect('works.sqlite')

    jobTitles = list(con.execute(f'SELECT jobTitle FROM works'))
    qualifications = list(con.execute(f'SELECT qualification FROM works'))
    con.close()

    people_count = count(jobTitles, qualifications)
    managers = works[works["jobTitle"].str.contains("менеджер")]
    top_managers = managers['qualification'].value_counts().head(5).index.values.tolist()
    engineers = works[works["qualification"].str.contains("инженер")]
    top_engineers = engineers['jobTitle'].value_counts().head(5).index.values.tolist()
    return render_template('topJobs.html',
                           all_count=all_count,
                           people_count=people_count,
                           top_managers=top_managers,
                           top_engineers=top_engineers)

def top(top_size, field_to_search, field_to_return, str_to_search):
    result = ''
    result_array = []
    for (f1, f2) in zip(field_to_search, field_to_return):
        if str(f1[0]).lower().find(str_to_search[:-2]) != -1:
            if str(f2[0]).find('None') == -1:
                result_array.append(f1[0])
    for i in range(top_size):
        result += f"<p>- {result_array[i][0]} - {result_array[i][1]} чел.</p>"
    return result

def count(field1, field2):
    result = 0
    total = 0
    for f1, f2 in zip(field1, field2):
        total += 1
        if not match(f1[0], f2[0]) and not match(f2[0], f1[0]):
            result += 1
    return result,total

def match(f1, f2):
    array = str(f1).lower().replace('-', ' ').split()
    for word in array:
        if word in str(f2).lower():
            return True
    return False

app.run()