from flask import Flask
from flask import render_template
from flask import Response
import sqlite3
import random
import io
from collections import Counter
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


@app.route("/stat")
def stat():
    con = sqlite3.connect('works.sqlite')
    jobs = list(con.execute(f'select jobTitle from works'))
    qualifications = list(con.execute(f'select qualification from works'))
    con.close()
    answer = 0
    all = 0
    for (job, qualification) in zip(jobs, qualifications):
        all += 1
        if not compare(str(job), str(qualification)) and not compare(str(qualification), str(job)):
            answer += 1
    res = f"<p>Из {all} людей не совпадают профессия и должность у {answer}</p>"
    res += f"<p>Топ 5 образований людей, которые работают менеджерами:</p>"
    res += get_top(jobs, qualifications, "менедж")
    res += f"<p>Топ 5 должностей людей, которые по диплому являются инженерами:</p>"
    res += get_top(qualifications, jobs, "инжен")
    return res


def get_top(profession, other, prof_name):
    answer = ''
    res = []
    for (prof, top_prof) in zip(profession, other):
        if str(prof[0]).lower().find(prof_name) != -1:
            if str(top_prof[0]).find('None') == -1:
                res.append(top_prof[0])
    full_top = Counter(res).most_common()
    for i in range(5):
        answer += f"<p>- {full_top[i][0]} - {full_top[i][1]} чел.</p>"
    return answer


def compare(profession, other):
    for i in profession.lower().replace('-', ' ').split():
        if i in other.lower():
            return True
    return False


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


app.run()
