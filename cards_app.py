from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from config import db_connect, create_tables

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
engine = db_connect()
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()


if __name__ == '__main__':
    app.run()