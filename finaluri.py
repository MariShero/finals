from flask import Flask, render_template, redirect, session, url_for
from flask import flash, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spidres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

base_name = sqlite3.connect("Biblus.sqlite")
base_name.row_factory = sqlite3.Row
cursor = base_name.cursor()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<users {self.id}, {self.Name}, {self.Surname}, {self.Email}>"

with app.app_context():
    db.create_all()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"books {self.id}, {self.title}, {self.price}"

with app.app_context():
    result = cursor.execute("SELECT * FROM Biblus")
    for row in result:
        new_book = Book(title=row['title'], price=row['price'])
        db.session.add(new_book)
        db.session.commit()
    db.create_all()

@app.route('/')
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)


@app.route("/register", methods=('POST', 'GET'))
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if password == confirm:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('მომხმარებელი უკვე არსებობს, გთხოვთ გაიაროთ ავტორიზაცია', 'warning')
                return redirect(url_for('login'))
            else:
                password_hash = generate_password_hash(password)
                new_user = User(name=name, surname=surname, email=email, password_hash=password_hash)
                db.session.add(new_user)
                db.session.commit()
                flash('თქვენ წარმატებით დარეგისტრირდით! გთხოვთ გაიაროთ ავტორიზაცია', 'success')
                return redirect(url_for("login"))
        else:
            flash("თქვენს მიერ შეყვანილი პაროლი არ ემთხვევა ზემოთ შეყვანილს, გთხოვთ შეიყვანოთ ხელახლა", 'error')
            return render_template("signup.html")

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            flash('თქვენ წარმატებით გაიარეთ ავტორიზაცია', 'success')
            return redirect(url_for('home'))
        else:
            flash('არასწორი ემაილი ან პაროლი, გთხოვთ სცადოთ ხელახლა.', 'error')

    return render_template('login.html')


@app.route('/add_book', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']

        new_book = Book(title=title, price=price)
        db.session.add(new_book)
        db.session.commit()
        flash('წიგნი წარმატებით დაემატა!', 'success')
        return redirect(url_for("home"))
    return render_template('add_book.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    flash("თქვენ გამოხვედით სისტემიდან, თუ გსურთ გაიარეთ ავტორიზაცია თავიდან", "warning")
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)