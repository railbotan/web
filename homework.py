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


def does_not_match_count(first_field, second_field):
    count = 0
    total = 0
    for (job_titles, qualifications) in zip(first_field, second_field):
        total += 1
        if not it_coincided(job_titles[0], qualifications[0]) and not it_coincided(qualifications[0], job_titles[0]):
            count += 1
    return count, total


def it_coincided(first_field, second_field):
    words = str(first_field).lower().replace('-', ' ').split()
    for word in words:
        if word in str(second_field).lower():
            return True
    return False


def get_top(first_field, second_field, search_word):
    result = []
    for (field1, field2) in zip(first_field, second_field):
        if str(field1[0]).lower().find(search_word[:-2]) != -1:
            if str(field2[0]).find('None') == -1:
                result.append(field2[0])
    return Counter(result).most_common()


def top_people(top_number, data, second_field, search_word):
    result = ''
    full_top_people = get_top(data, second_field, search_word)
    for i in range(top_number):
        result += f"<p>- {full_top_people[i][0]} - {full_top_people[i][1]} чел.</p>"
    return result


def get_list_field(field):
    con = sqlite3.connect('works.sqlite')
    result = list(con.execute(f'select {field} from works'))
    con.close()
    return result


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
    return render_template('d2.html', cvs=get_cv(), labels=[row[0] for row in res], data=[row[1] for row in res])


@app.route("/statistic")
def statistic():
    job_titles = get_list_field('jobTitle')
    qualifications = get_list_field('qualification')
    res = ""
    people_count = does_not_match_count(job_titles, qualifications)
    res += f"<p>Из {people_count[1]} людей не совпадают профессия и должность у {people_count[0]}</p>"
    res += f"<p>Топ 5 образований людей, которые работают менеджерами:</p>"
    res += get_top(5, job_titles, qualifications, "менеджер")
    res += f"<p>Топ 5 должностей людей, которые по диплому являются инженерами:</p>"
    res += get_top(5, qualifications, job_titles,  "инженер")
    return res


def dict_factory(cursor, row):
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
