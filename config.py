"""Configuration settings for Smart Study Scheduler."""

import os


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///study_scheduler.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
