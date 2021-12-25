import io
from flask import Flask
from flask import render_template
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from services import get_cv, get_count_by_year, create_random_figure, get_top_edu_by_job

app = Flask(__name__)


@app.route("/")
def cv_index():
    cvs = get_cv()
    res = ("\n".join((f"<h1>{i + 1})</h1>",
                      f"<p>Желаемая зарплата: {cv['salary']}.</p>",
                      f"<p>Образование: {cv['educationType']}.</p>")) for i, cv in enumerate(cvs))
    return "".join(res)


@app.route("/dashboard")
def dashboard():
    return render_template('d3.html', cvs=get_cv())


@app.route("/years")
def years():
    cvs = get_count_by_year()
    data = [cv["count"] for cv in cvs]
    labels = [cv["year"] for cv in cvs]
    return render_template('d4.html', cvs=cvs, data=data, labels=labels)


@app.route("/edu/managers")
def edu_managers():
    cvs = get_top_edu_by_job(("manager", "менедж"))
    data = [cv["count"] for cv in cvs]
    labels = [cv["qualification"] for cv in cvs]
    return render_template('d5.html', cvs=cvs, data=data, labels=labels, ql="менеджеров")


@app.route("/edu/engineer")
def edu_engineers():
    cvs = get_top_edu_by_job(("engineer", "инжене"))
    data = [cv["count"] for cv in cvs]
    labels = [cv["qualification"] for cv in cvs]
    return render_template('d5.html', cvs=cvs, data=data, labels=labels, ql="инженеров")


@app.route('/plot.png')
def plot_png():
    output = io.BytesIO()
    FigureCanvas(create_random_figure()).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
