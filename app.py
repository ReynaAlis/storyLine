from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, User, Post
from forms import RegistrationForm, LoginForm 
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
app.secret_key = 'supersecretkey'
db.init_app(app)  
bcrypt = Bcrypt(app)

@app.route("/search")
def search():
    query = request.args.get('query', '')
    if query:
        results = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) |
            (Post.text.ilike(f'%{query}%'))
        ).all()
    else:
        results = []
    return render_template('search_results.html', results=results, query=query)

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/posts")
def posts():
    post = Post.query.all()
    return render_template('posts.html', posts = post )

@app.route("/create", methods=["POST", "GET"])
def create():
    if not session.get('user_id'):  
        flash('Вы должны войти в систему, чтобы добавить статью.', 'warning')
        return redirect(url_for('login'))

    if request.method == "POST":
        title = request.form['title'].strip()
        text = request.form['text']

        if not title or not text:
            flash("Заголовок и текст статьи не могут быть пустыми", "error")
            return render_template('create.html', title=title, text=text)

        post = Post(title=title, text=text, author=session['username']) 

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/posts')
        except: 
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template('create.html')

@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != session.get('username'):
        flash("У вас нет прав для редактирования этой статьи.", "danger")
        return redirect(url_for('posts'))

    if request.method == "POST":
        title = request.form['title'].strip()
        text = request.form['text'].strip()

        if not title or not text:
            flash("Заголовок и текст статьи не могут быть пустыми", "danger")
        else:
            post.title = title
            post.text = text
            post.last_modified = datetime.now(timezone.utc)
            db.session.commit()
            flash("Статья успешно обновлена!", "success")
            return redirect(url_for('post_detail', post_id=post.id))  

    return render_template('edit_post.html', post=post)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Ваш аккаунт создан! Теперь вы можете войти.', 'success')
        return redirect(url_for('login')) 
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session.clear()

            session['user_id'] = user.id 
            session['username'] = user.username  

            flash(f'Вы вошли как {user.username}!', 'success')
            return redirect(url_for('index'))  
        else:
            flash('Неверная почта или пароль. Попробуйте снова.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    session.clear()  
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
