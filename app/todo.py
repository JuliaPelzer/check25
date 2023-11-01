from flask import Blueprint, flash, g, render_template, request, url_for, session

from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint('todo', __name__)

@bp.route('/')
def index():
    db = get_db()
    items = db.execute("SELECT * FROM task WHERE user_id == ?", "1").fetchall()
    return render_template('todo/index.html', items=items)

@bp.route('/add', methods = ["POST"])
def add():
    db = get_db()
    done = request.args["done"]
    text = request.args["text"]
    user_id = session.get("user_id")

    db.execute("INSERT INTO task (user_id, done, text) VALUES (?, ?, ?)", (user_id, done, text))
    db.commit()

    return {"status" : "Task Added"}

