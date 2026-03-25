"""Database models for Smart Study Scheduler."""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance initialized in app.py

db = SQLAlchemy()


class User(db.Model):
    """User account model."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relationship to tasks
    tasks = db.relationship("Task", backref="user", lazy=True, cascade="all, delete-orphan")


class Task(db.Model):
    """Study task model."""

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(20), nullable=False, default="Pending")

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
