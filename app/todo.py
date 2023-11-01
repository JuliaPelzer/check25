from flask import Blueprint, flash, g, render_template, request, url_for, session

from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint('todo', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    user_id = str(session.get("user_id"))
    items = db.execute("SELECT * FROM task WHERE user_id == ?", user_id).fetchall()
    return render_template('todo/index.html', items=items)

@bp.route('/add', methods = ["POST"])
@login_required
def add():
    db = get_db()
    done = request.args["done"]
    text = request.args["text"]
    user_id = session.get("user_id")

    db.execute("INSERT INTO task (user_id, done, text) VALUES (?, ?, ?)", (user_id, done, text))
    db.commit()

    return {"status" : "Task Added"}

