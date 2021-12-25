import io
import random
import sqlite3
import pandas as pd

from flask import Flask
from flask import Response
from collections import Counter
from flask import render_template
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

application = Flask(__name__)

@application.route("/")
def index_cv():
    cvs = get_cv()
    result = ""
    for i, cv in enumerate(cvs):
        result += f"<h1>{i + 1})</h1>"
        result += f"<p>Желаемая зарплата: {cv['salary']}.</p>"
        result += f"<p>Образование: {cv['educationType']}.</p>"
    return result

@application.route("/dashboard")
def dashboard():
    connected = sqlite3.connect('works.sqlite')
    result = connected.execute('SELECT SUBSTR(dateModify, 1, 4), COUNT(*) FROM works WHERE dateModify NOT NULL GROUP BY '
                      'SUBSTR(dateModify, 1, 4)').fetchall()
    connected.close()
    return render_template('d2.html',
                           cvs = get_cv(),
                           labels = [row[0] for row in result],
                           data = [row[1] for row in result])

@app.route("/statistic")
def statistic():
    jobTitles = get_list_field('jobTitle')
    qualifications = get_list_field('qualification')
    result = ""
    peop_count = count_people_field1_not_match_field2(jobTitles, qualifications)
    res += f"<p>Из {peop_count[1]} людей не совпадают профессия и должность у {peop_count[0]}</p>"
    res += f"<p>Топ 5 образований людей, которые работают менеджерами:</p>"
    res += get_top(5, jobTitles, qualifications, "менеджер")
    res += f"<p>Топ 5 должностей людей, которые по диплому являются инженерами:</p>"
    res += get_top(5, qualifications, jobTitles,  "инженер")
    return result

def get_top(top_size, field_to_search, field_to_return, str_to_search):
    result = ''
    full_top = top(field_to_search, field_to_return, str_to_search)
    for i in range(top_size):
        result += f"<p>- {full_top[i][0]} - {full_top[i][1]} чел.</p>"
    return result


def get_list_field(field):
    connected = sqlite3.connect('works.sqlite')
    result = list(connected.execute(f'select {field} from works'))
    connected.close()
    return result

def factor_dict(cursor, row):
    d = {}
    for index, col in enumerate(cursor.description):
        d[col[0]] = row[index]
    return d

def get_cv():
    connected = sqlite3.connect('works.sqlite')
    connected.row_factory = factor_dict
    result = list(connected.execute('select * from works limit 20'))
    connected.close()
    return result

@application.route('/plot.png')
def plot_png():
    figur = create_figure()
    output = io.BytesIO()
    FigureCanvas(figur).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    figur = Figure()
    axis = figur.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return figur

def count_people_field1_not_match_field2(field1, field2):
    res_count = 0
    total = 0
    for (f1, f2) in zip(field1, field2):
        total += 1
        if not find_match(f1[0], f2[0]) and not find_match(f2[0], f1[0]):
            res_count += 1
    return res_count, total

def find_match(f1, f2):
    arr1 = str(f1).lower().replace('-', ' ').split()
    for word in arr1:
        if word in str(f2).lower():
            return True
    return False

def top(f_to_search, f_to_return, str_to_search):
    result = []
    for (f_s, f_r) in zip(f_to_search, f_to_return):
        if str(f_s[0]).lower().find(str_to_search[:-2]) != -1:
            if str(f_r[0]).find('None') == -1:
                result.append(f_r[0])

    return Counter(result).most_common()

application.run()