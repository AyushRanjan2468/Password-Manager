from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Signup successful!")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return redirect(url_for("password_manager"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/add", methods=["GET", "POST"])
def password_manager():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username and password:
            with open("passwords.txt", 'a') as f:
                f.write(f"{username} {password}\n")
            flash("Password added successfully!")
            return redirect(url_for("password_manager"))
        else:
            flash("Please enter both the fields", 400)
    return render_template("password_manager.html")

@app.route("/get", methods=["POST"])
def get_password():
    username = request.form["username"]
    passwords = {}
    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                passwords[i[0]] = i[1]
    except:
        return "ERROR!!", 500
    if passwords:
        mess = "Your passwords:\n"
        for i in passwords:
            if i == username:
                mess += f"Password for {username} is {passwords[i]}\n"
                break
        else:
            mess += "No Such Username Exists!!"
        return mess
    else:
        return "EMPTY LIST!!", 404
@app.route("/list", methods=["GET"])
def list_passwords():
    passwords = {}
    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                passwords[i[0]] = i[1]
    except:
        return "No passwords found!!", 404

    if passwords:
        mess = "List of passwords:\n"
        for name, password in passwords.items():
            mess += f"Password for {name} is {password}\n"
        return mess
    else:
        return "Empty List!!", 404

@app.route("/delete", methods=["POST"])
def delete_password():
    username = request.form["username"]
    temp_passwords = []
    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                if i[0]!= username:
                    temp_passwords.append(f"{i[0]} {i[1]}")
        with open("passwords.txt", 'w') as f:
            for line in temp_passwords:
                f.write(line)
        flash(f"User {username} deleted successfully!")
        return redirect(url_for("password_manager"))
    except Exception as e:
        flash(f"Error deleting user {username}: {e}", 500)
        return redirect(url_for("password_manager"))

@app.route("/generate", methods=["GET"])
def generate_password():
    password_length = 8
    password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(password_length))
    return render_template("generate_password.html", password=password)

@app.route("/clear", methods=["GET"])
def clear_fields():
    return render_template("password_manager.html")

@app.route("/change_password", methods=["GET"])
def change_password():
    return render_template("change_password.html")

@app.route("/update_password", methods=["POST"])
def update_password():
    username = request.form["username"]
    old_password = request.form["old_password"]
    new_password = request.form["new_password"]
    temp_passwords = []
    try:
        with open("passwords.txt", 'r') as f:
            for k in f:
                i = k.split(' ')
                if i[0] == username and i[1].strip() == old_password:
                    temp_passwords.append(f"{i[0]} {new_password}\n")
                else:
                    temp_passwords.append(k)
        with open("passwords.txt", 'w') as f:
            for line in temp_passwords:
                f.write(line)
        flash(f"Password for {username} updated successfully!")
        return redirect(url_for("password_manager"))
    except Exception as e:
        flash(f"Error updating password for {username}: {e}", 500)
        return redirect(url_for("password_manager"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
