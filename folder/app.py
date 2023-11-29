from flask import Flask, render_template, redirect, url_for, request, session, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(10)) 
    postcode = db.Column(db.String(10))
    bio = db.Column(db.Text)


@app.route('/')
def home():
    return 'Welcome to the home page!'


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            session['user'] = username
            return redirect(url_for('profile'))
        else:
            return 'Invalid username. Please try again.'
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user' in session:
        username = session['user']
        user = User.query.filter_by(username=username).first()
        return render_template('profile.html', user=user)
    else:
        return 'You are not logged in. Please log in.'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

