from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from config import db_connect, create_tables
from flask_login import LoginManager
import os.path
login_manager = LoginManager()

app = Flask(__name__)
app.config.from_pyfile(os.path.dirname(__file__) + '/../config.py')
db = SQLAlchemy(app)
engine = db_connect()
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()
login_manager.init_app(app)


if __name__ == '__main__':
    app.run()