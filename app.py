from flask import Flask, jsonify, request, g, render_template, redirect
from flask_cors import CORS
from werkzeug import exceptions
import sqlite3
from controllers import urls

from url_generator import creator

app = Flask(__name__)
CORS(app)

DATABASE = "./database/database.db"

@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    fetch_url = request.form['url']
    generated_url = creator.create_url()
    urls.create(generated_url, fetch_url)
    return render_template('home.html', url=generated_url)
  else:
    return render_template('home.html')

@app.route('/<string:short_url>', methods=['GET'])
def redirect_user(short_url):
  url = urls.find_by_id(short_url)
  return redirect(url[0][0])

@app.errorhandler(exceptions.NotFound)
def handle_404(error):
  return render_template('errors/404.html'), 404  

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()

def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
      print("Initialised DB")
    db.commit()

def query_db(query, args=(), one=False):
  cur = get_db().execute(query, args)
  get_db().commit()
  rv = cur.fetchall()
  cur.close()
  return (rv[0] if rv else None) if one else rv

if __name__ == "__main__":
    app.run(debug=True)