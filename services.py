import sqlite3
import random
from matplotlib.figure import Figure

DB_NAME = 'works.sqlite'


def _ignore_case_collation(value1_, value2_):
    value1_, value2_ = str(value1_), str(value2_)
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1


def get_connection():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    # Изначально sqlite работает только с ASCII символами.
    con.create_collation("BINARY", _ignore_case_collation)
    con.create_collation("NOCASE", _ignore_case_collation)
    con.create_function("LOWER", 1, lambda value_: str(value_).lower())
    con.create_function("UPPER", 1, lambda value_: str(value_).upper())

    return con


def get_cv():
    query = "SELECT * FROM works LIMIT 20"
    with get_connection() as con:
        return list(con.execute(query))


def get_count_by_year():
    query = ("SELECT COUNT(*) as 'count', strftime('%Y', dateModify) as 'year' "
             "FROM works WHERE year IS NOT NULL GROUP BY year")
    with get_connection() as con:
        return list(con.execute(query))


def get_top_edu_by_job(job_titles: tuple[str, str], count: int = 15):
    query = (f"SELECT LOWER(qualification) as 'qualification', count(*) as 'count' FROM works "
             f"WHERE qualification IS NOT NULL AND "
             f"(LOWER(jobTitle) like '%{job_titles[0]}%' OR LOWER(jobTitle) like '%{job_titles[1]}%')"
             f"GROUP BY LOWER(qualification) "
             f"ORDER BY count DESC LIMIT {count}")
    with get_connection() as con:
        return list(con.execute(query))


def create_random_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for _ in xs]
    axis.plot(xs, ys)

    return fig
