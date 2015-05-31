from flask import Flask
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

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
