from flask import Blueprint, flash, g, render_template, request, url_for, session

from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint("todo", __name__)


@bp.route("/")
@login_required
def index():
    db = get_db()
    user_id = str(session.get("user_id"))
    items = db.execute("SELECT * FROM task WHERE user_id == ?", (user_id,)).fetchall()
    return render_template("todo/index.html", items=items)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    db = get_db()
    done = request.args["done"]
    text = request.args["text"]
    user_id = session.get("user_id")

    cur = db.cursor()
    cur.execute(
        "INSERT INTO task (user_id, done, text) VALUES (?, ?, ?)", (user_id, done, text)
    )
    db.commit()
    id = cur.lastrowid

    return {"status": "Task Added", "id": id}


@bp.route("/delete", methods=["DELETE"])
@login_required
def delete():
    db = get_db()
    id = request.args["id"]
    user_id = session.get("user_id")
    task_owner = db.execute("SELECT user_id FROM task WHERE id == ?", (id,)).fetchone()[
        "user_id"
    ]

    if task_owner != user_id:
        return {"status": "Task not found"}

    db.execute("DELETE FROM task WHERE id=?", (id,))
    db.commit()

    return {"status": "Task Deleted"}
