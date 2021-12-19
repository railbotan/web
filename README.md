# Flask

Flask позволяет создавать динамические веб-приложения. В простейшем случае Flask служит абстракцией над протоколом HTTP, позволяя вызывать функцию с некоторыми параметрами, а отвечать веб-страницей (HTML-файлом).

## 1. Самая простая страница

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Привет!</p>"

app.run()
```

Если  запустить этот скрипт, запустится разработческий веб-сервер по умолчанию на 5000 порту, т.е. результат можно посмотреть в браузере по ссылке http://127.0.0.1:5000/, о чем нам и сообщает Flask:

```
 * Serving Flask app "job" (lazy loading)
 * Environment: production
WARNING: This is a development server. Do not use it in a production deployment.
Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 ```
 
Надо понимать, что в условном продакшене нужна другая схема запуска, например, через  WSGI, например, используя [Gunicorn](https://gunicorn.org/). Мы будем обходиться отладочным, разработческим сервером.

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

Эта веб-страница будет  показывать текущее время при перезагрузке.

## 3. Добавим соединение с базой данных

Фактически, на главной странице мы увидим словари с первыми 3 записями в таблице `works`.

```python
from flask import Flask
from datetime import datetime
import sqlite3


app = Flask(__name__)

@app.route("/")
def hello_world():
    return str(list(get_cv()))


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
