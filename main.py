from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import math
import json

with open("config.json", "r") as c:
    params = json.load(c)['params']

local_server = True
app = Flask(__name__)

app.secret_key = params['secret_key']

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
    content = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    img_file = db.Column(db.String(25), nullable=False)
    sub_title = db.Column(db.String(100), nullable=False)


@app.route('/')
def index():  # [0:params['no_of_posts']]
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))

    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1

    page = int(page)

    posts = posts[(page - 1) * int(params['no_of_posts']): (page - 1) * int(params['no_of_posts'])
                                                           + int(params['no_of_posts'])]

    if page == 1:
        prev = '#'
        next = '/?page=' + str(page + 1)

    elif page == last:
        prev = '/?page=' + str(page - 1)
        next = '#'

    else:
        prev = '/?page=' + str(page - 1)
        next = '/?page=' + str(page + 1)

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route('/dashboard', methods=['GET', 'POST'])
def admin():

    posts = Post.query.all()

    if 'user' in session and session['user'] == params['login_username']:   # if user already logged in
        return render_template('main_dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == params['login_username'] and password == params['login_password']:
            # set the session variable
            session['user'] = username
            return render_template('main_dashboard.html', params=params, posts=posts)

    else:
        return render_template('dashboard.html', params=params)


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['login_username']:
        post = Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()

        return redirect('/dashboard')


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['login_username']:
        if request.method == 'POST':
            new_title = request.form.get('title')
            new_sub_title = request.form.get('sub_title')
            new_slug = request.form.get('slug')
            new_content = request.form.get('content')
            new_img_file = request.form.get('img_file')

            if sno == '0':
                post = Post(title=new_title, slug=new_slug, content=new_content,
                            sub_title=new_sub_title, img_file=new_img_file, date=datetime.now())
                db.session.add(post)
                db.session.commit()

            else:
                post = Post.query.filter_by(sno=sno).first()
                post.title = new_title
                post.slug = new_slug
                post.content = new_content
                post.img_file = new_img_file
                post.sub_title = new_sub_title
                db.session.commit()
                return redirect('/edit/' + sno)
        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


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
