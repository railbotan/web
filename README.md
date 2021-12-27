# Flask

Flask позволяет создавать динамические веб-приложения. В простейшем случае Flask служит абстракцией над протоколом HTTP,
позволяя вызывать функцию с некоторыми параметрами, а отвечать веб-страницей (HTML-файлом).

Мы попробуем сделать прототип сервера статистики с резюме. Но начнем с простого.

## 1. Самая простая страница

```python
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Привет!</p>"


app.run()
```

Если запустить этот скрипт, запустится разработческий веб-сервер по умолчанию на 5000 порту, т.е. результат можно
посмотреть в браузере по ссылке http://127.0.0.1:5000/, о чем нам и сообщает Flask:

```
 * Serving Flask app "job" (lazy loading)
 * Environment: production
WARNING: This is a development server. Do not use it in a production deployment.
Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 ```

Надо понимать, что в условном продакшене нужна другая схема запуска, например, через WSGI, например,
используя [Gunicorn](https://gunicorn.org/). Мы будем обходиться отладочным, разработческим сервером.

## 2. Когда видно, что страница динамическая

Давайте сделаем контент чуть динамичнее:

```python
from flask import Flask
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def hello_world():
    return f"<p>{datetime.now()}</p>"


app.run()
```

Эта веб-страница будет показывать текущее время при перезагрузке.

## 3. Добавим соединение с базой данных

Фактически, на главной странице мы увидим словари с первыми 3 записями в таблице `works`.

```python
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

```

## 4. А какже верстка, всякие теги?

Добавим верстки. По факту, функция  `hello_world` (на этом моменте ее надо бы переназвать) должна просто свормировать
строку с html-разметкой. Давайте сделаем это в ручном режиме.

```python
from flask import Flask
from datetime import datetime
import sqlite3

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
```

Да, теперь мы используем разметку, страница стала выглядеть лучше. Но есть два момента:

* Дизайн элементов по умолчанию в браузере выглядит ужасно.
* Наш файл превращается в монстра, который контролирует все, включая ужасное с архитектурной точки зрения формирование
  HTML.

Попробуем по очереди исправить это.

## 5. Внешние шаблоны. d1.html

За основу давайте возьмем пример [дашборда](https://getbootstrap.com/docs/5.1/examples/dashboard/#) из библиотеки стилей
и скриптов Bootstrap. Я немного изменил его, чтобы он мог открываться локально. Файл `templates/d1.html`.

```python
from flask import Flask
from flask import render_template
from datetime import datetime
import sqlite3

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
    return render_template('d1.html')


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
```

Мы создали новую функцию `dashboard`, которая отвечает по урлу http://127.0.0.1:5000/dashboard

Внешний шаблон с HTML &mdash; это удобно.

## 6. Наши данные в шаблоне. d2.html

Давайте сделаем несколько косметических изменений в шаблоне:

```html
<a class="navbar-brand col-md-3 col-lg-2 me-0 px-3" href="#">Company name</a>
```

Превратится в

```html
<a class="navbar-brand col-md-3 col-lg-2 me-0 px-3" href="#">База резюме</a>
```

Изменим столбцы в таблице:

```html

<table class="table table-striped table-sm">
    <thead>
    <tr>
        <th scope="col">#</th>
        <th scope="col">Зарплата</th>
        <th scope="col">Образование</th>
        <th scope="col">Пол</th>
    </tr>
    </thead>
    <tbody>
    <tr>
```

Передадим в шаблон переменную `cvs`:

```python
@app.route("/dashboard")
def dashboard():
    return render_template('d2.html',
                           cvs=get_cv(),
                           )
```

Во Flask используется специальный язык шаблонов, такой неполноценный (специально) мини-язык программирования, в котором
есть условия, циклы, фильтры и доступ к глобальным переменным, переданным в шаблон.

```html

<tbody>
{% for cv in cvs %}
<tr>
    <td>{{ loop.index }}</td>
    <td>{{ cv.salary }}</td>
    <td>{{ cv.educationType }}</td>
    <td>{{ cv.gender }}</td>
</tr>
{% endfor %}
</tbody>
```

Обратите внимание на специальную переменную `loop.index`. Произошло разделение функциональности: в Python мы берем
данные, обрабатываем их, а в шаблоне управляем показом. Именно поэтому язык шаблонов ограничен. Это сделано, чтобы в
него не проникала бизнес-логика.

Код на Python в итоге такой:

```python
from flask import Flask
from flask import render_template
from datetime import datetime
import sqlite3

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
    return render_template('d2.html',
                           cvs=get_cv(),
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


app.run()
```

## 7. Отдаем картинку. d3.html

Мы можем по какой-то ссылке отдавать не только html, но и любой файл, сообщая браузеру его тип. Например, байтовую
последовательность картинки, полученной в `matplotlib`. Пример
взят [отсюда](https://stackoverflow.com/questions/50728328/python-how-to-show-matplotlib-in-flask).

```python
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
```

А в шаблоне указать после таблицы изображение:

```html
  </tbody>
</table>
<img src="/plot.png"/>
</div>
```

Полностью код:

```python
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
    return render_template('d3.html',
                           cvs=get_cv(),
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


app.run()
```

## Задания:

### 1.

На странице сверху используется js-построитель графика. Попробуйте заменить его на количество резюме по годам.

Это вот в этом месте шаблона:

```html
data: {
labels: [
'Sunday',
'Monday',
'Tuesday',
'Wednesday',
'Thursday',
'Friday',
'Saturday'
],
datasets: [{
data: [
15339,
21345,
18483,
24003,
23489,
24092,
12034
],
```

### 2.

Выведите часть из прошлой статистики по полям из занятий по анализу данных и SQL.
