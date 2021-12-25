import os
import sqlite3
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from flask import Flask
from flask import render_template
from flask import Response
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

con = sqlite3.connect("task.sqlite")
cursor = con.cursor()

cursor.execute("drop table if exists works")
cursor.execute("create table works("
               "ID integer primary key AUTOINCREMENT,"
               "salary integer,"
               "educationType text,"
               "jobTitle text,"
               "qualification text,"
               "gender text,"
               "dateModify text,"
               "skills text,"
               "otherInfo text"
               ");")
con.commit()

data = pd.read_csv("works.csv")
data.to_sql('works', con, if_exists="append", index = None)
con.commit()


a = cursor.execute("select substring(dateModify, 1, 4) as 'year', count(*) as 'c' from works group by year").fetchall()
labels = list(map(lambda x: x[0], a))
values = list(map(lambda x: x[1], a))
mensCount = cursor.execute("select count(*) from works where gender = 'Мужской'").fetchall()[0][0]
womensCount = cursor.execute("select count(*) from works where gender = 'Женский'").fetchall()[0][0]

# 1ый график
'''cursor.execute("select salary from works where gender = 'Мужской'")
men = list(map(lambda row: row[0],cursor.fetchall()))
cursor.execute("select salary from works where gender = 'Женский'")
women = [row[0] for row in cursor.fetchall()]
pers = np.linspace(0.1, 1, 10)
a = np.quantile(men, pers)
b = np.quantile(women, pers)
plt.plot(pers, a, color="b")
plt.plot(pers, b, color="r")
plt.xlabel("Перцентили")
plt.ylabel("Зарплата")
plt.show()'''

# 2ой график
'''cursor.execute("select educationType, avg(salary) as 'av' from works where gender='Мужской' group by educationType")
men = list(map(lambda row: row[1],cursor.fetchall()))[1:5]
print(men)
cursor.execute("select educationType, avg(salary) as 'av' from works where gender='Женский' group by educationType")
women = list(map(lambda row: row[1],cursor.fetchall()))[1:5]
print(women)
index = np.arange(4)
bw = 0.3
plt.bar(index, men, bw, color='b')
plt.bar(index+bw, women, bw, color='r')
plt.xticks(index+0.5*bw,['Высшее','Неоконченное высшее','Среднее','Проффессиональное'])
plt.show()'''


app = Flask(__name__, static_folder="C:\\Users\\Иван\\Documents\\pRep\\web")


@app.route("/")
def cv_index():
    return render_template('myPage.html', count=sum(values), mensCount=mensCount, womensCount=womensCount)


@app.route("/dashboard")
def dashboard():
    return render_template('d3.html',
                           cvs=get_cv(), labels=labels[1:4], values=values[1:4],
                           )


def dict_factory(cursor, row):
    # обертка для преобразования
    # полученной строки. (взята из документации)
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_cv():
    con = sqlite3.connect('task.sqlite')
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
    xs = [2000, 2001, 2002]
    ys = [300, 50, 70]
    axis.plot(xs, ys)
    return fig

app.run()