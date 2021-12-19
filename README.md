# Flask

Flask позволяет создавать динамические веб-приложения. В простейшем случае Flask служит абстракцией над протоколом HTTP, позволяя вызывать функцию с некоторыми параметрами, а отвечать веб-страницей (HTML-файлом).

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

