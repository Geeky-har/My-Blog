from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from flask_mail import Mail
import json

with open("config.json", "r") as c:
    params = json.load(c)['params']

local_server = True
app = Flask(__name__)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['user-email'],
    MAIL_PASSWORD=params['user-password']
)

mail = Mail(app)

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    message = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(25), nullable=False)


class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(15), nullable=False)
    content = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    img_file = db.Column(db.String(25), nullable=False)


@app.route('/')
def index():
    return render_template('index.html', params=params)


@app.route('/about')
def about():
    return render_template('about.html', params=params)


@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    post_first = Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html', post_first=post_first, params=params)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(name=name, phone=phone, message=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message(
            'New Message from' + name,
            sender=email,
            recipients=[params['user-email']],
            body = message + '\n' + phone
        )

    return render_template('contact.html', params=params)


if __name__ == "__main__":
    app.run(debug=True)
