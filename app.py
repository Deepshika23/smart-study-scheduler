"""Main Flask application for Smart Study Scheduler."""

from datetime import datetime, timedelta

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from models import Task, User, db
from scheduler import optimize_schedule


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


with app.app_context():
    db.create_all()


def current_user():
    """Return currently logged-in user object from session."""

    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required():
    """Helper to enforce authentication in routes."""

    if not current_user():
        flash("Please log in to continue.", "warning")
        return redirect(url_for("login"))
    return None


@app.route("/")
def index():
    """Landing route redirects based on auth state."""

    if current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username is already taken.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        user = User(username=username, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate and start a session."""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """End user session."""

    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    """Display user tasks and upcoming deadlines."""

    auth_redirect = login_required()
    if auth_redirect:
        return auth_redirect

    user = current_user()

    selected_priority = request.args.get("priority", "")

    query = Task.query.filter_by(user_id=user.id)
    if selected_priority in {"High", "Medium", "Low"}:
        query = query.filter_by(priority=selected_priority)

    tasks = query.all()
    optimized_tasks = optimize_schedule(tasks)

    now = datetime.utcnow()
    upcoming_cutoff = now + timedelta(days=7)
    upcoming_tasks = (
        Task.query.filter(
            Task.user_id == user.id,
            Task.status == "Pending",
            Task.deadline >= now,
            Task.deadline <= upcoming_cutoff,
        )
        .order_by(Task.deadline.asc())
        .all()
    )

    return render_template(
        "dashboard.html",
        user=user,
        tasks=optimized_tasks,
        selected_priority=selected_priority,
        upcoming_tasks=upcoming_tasks,
    )


@app.route("/add-task", methods=["POST"])
def add_task():
    """Create a new task for current user."""

    auth_redirect = login_required()
    if auth_redirect:
        return auth_redirect

    user = current_user()

    subject = request.form.get("subject", "").strip()
    deadline_raw = request.form.get("deadline", "").strip()
    priority = request.form.get("priority", "Medium")

    if not subject or not deadline_raw:
        flash("Subject and deadline are required.", "danger")
        return redirect(url_for("dashboard"))

    if priority not in {"High", "Medium", "Low"}:
        priority = "Medium"

    try:
        deadline = datetime.strptime(deadline_raw, "%Y-%m-%dT%H:%M")
    except ValueError:
        flash("Invalid deadline format.", "danger")
        return redirect(url_for("dashboard"))

    task = Task(
        subject=subject,
        deadline=deadline,
        priority=priority,
        status="Pending",
        user_id=user.id,
    )
    db.session.add(task)
    db.session.commit()

    flash("Task added successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/complete-task/<int:task_id>")
def complete_task(task_id):
    """Mark a task as completed."""

    auth_redirect = login_required()
    if auth_redirect:
        return auth_redirect

    user = current_user()

    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    task.status = "Completed"
    db.session.commit()

    flash("Task marked as completed.", "success")
    return redirect(url_for("dashboard"))


@app.route("/delete-task/<int:task_id>")
def delete_task(task_id):
    """Delete a user task."""

    auth_redirect = login_required()
    if auth_redirect:
        return auth_redirect

    user = current_user()

    task = Task.query.filter_by(id=task_id, user_id=user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully.", "info")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
