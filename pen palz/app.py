"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template, request, session, g, redirect
from helpers import login_required,read_file_lines
from flask_session import Session
import hashlib
from cs50 import SQL
import os
from routes.find import find_bp

db = SQL("sqlite:///users.db")
app = Flask(__name__)
app.register_blueprint(find_bp)

@app.before_request
def check_session():
    if "user_id" in session:
        user_id = session["user_id"]
        if not isinstance(user_id, int):
            session.clear()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
Session(app)
wsgi_app = app.wsgi_app

@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("login.html",result = "Must provide username")

        elif not request.form.get("password"):
            return render_template("login.html",result = "Must provide password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if rows == []:
            return render_template("login.html",result = "Username not found")
        password = db.execute("SELECT password_hash FROM users WHERE username = ?", [request.form.get("username")])
        print(rows)
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def registration():
    countries = read_file_lines("data\countries.txt")
    if request.method == "POST":

        if not request.form.get("firstName"):
            return redirect("/error")
        if not request.form.get("lastName"):
           return redirect("/error")
        if not request.form.get("username"):
           return redirect("/error")
        if not request.form.get("password"):
             return redirect("/error")
        if not request.form.get("confirmation"):
            return redirect("/error")
        rows = db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        if rows != []:
            return render_template("registration.html", result = "Username already taken", countries = countries)
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("registration.html", result = "Passwords do not match", countries = countries)
        hashed = hash_password(request.form.get("password"))
        db.execute("INSERT INTO users (first_name,last_name,username,password_hash) VALUES (?,?,?,?)", request.form.get("firstName"), request.form.get("lastName"),request.form.get("username"), hashed)
        return redirect("/")
    else:
        return render_template("registration.html", countries = countries)

@app.route('/error')
def error():
    return render_template("error.html")


@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "GET":
        profilePicFilename = db.execute("SELECT profile_picture_filename FROM UserProfile where user_id == ?", session["user_id"])
        userDescription = db.execute("SELECT user_description FROM UserProfile where user_id == ?", session["user_id"])
        if profilePicFilename == [] and userDescription == []:
            return render_template('profile.html')
        elif profilePicFilename == []:
            return render_template('profile.html', initialText = userDescription[0]["user_description"])
        elif userDescription == []:
            return render_template('profile.html', profilePicture = profilePicFilename[0]["profile_picture_filename"])
        return render_template('profile.html', initialText = userDescription[0]["user_description"], profilePicture = profilePicFilename[0]["profile_picture_filename"])
    else:
        description = request.form.get("description")
        check = db.execute ("SELECT * FROM UserProfile WHERE user_id = ?", session["user_id"])
        if check == []:
            db.execute("INSERT INTO UserProfile (user_id, profile_picture_filename, user_description) VALUES (?, ?, ?)",session["user_id"],None,None)

        db.execute("UPDATE UserProfile SET user_description = ? WHERE user_id = ?", description, session["user_id"])

        if 'file' not in request.files:
            return redirect(request.url)
    
        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            file_extension = os.path.splitext(file.filename)[1]
            filename = os.path.join(app.config['UPLOAD_FOLDER'], str(session["user_id"])+ file_extension)
            file.save(filename)
            db.execute("UPDATE UserProfile SET profile_picture_filename = ? WHERE user_id = ?", filename, session["user_id"])
            
        return redirect("/profile")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/message/<username>', methods=["GET", "POST"])
@login_required
def message(username):
    recipientId = db.execute("SELECT id FROM users WHERE username == ?", username)
    recipientId = recipientId[0]['id']
    user = db.execute("SELECT * from users WHERE username = ?", username)
    if request.method == "GET":
        
        db.execute("INSERT OR IGNORE INTO matches(id,user1_id,user2_id) VALUES (?,?,?)", session["user_id"],session["user_id"],recipientId)
        messageHistory = db.execute("SELECT sender_id, receiver_id, message_content, timestamp FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)", session["user_id"], recipientId, recipientId, session["user_id"])
        if user != []:
            db.execute 
            return render_template('message.html', user = user[0], messages = messageHistory)
        else:
            return "User not found"
    else:
        message = request.form.get("message")
        print(message)
        db.execute("INSERT INTO messages (sender_id,receiver_id, message_content,timestamp) VALUES (?,?,?,CURRENT_TIMESTAMP)", session["user_id"],recipientId,message)
        messageHistory = db.execute("SELECT sender_id, receiver_id, message_content, timestamp FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)", session["user_id"], recipientId, recipientId, session["user_id"])
        for item in messageHistory:
            print(item)
        return render_template('message.html', user = user[0], messages = messageHistory)


def hash_password(password):
    hasher = hashlib.sha256()
    hasher.update(password.encode('utf-8'))
    hashed_password = hasher.hexdigest()

    return hashed_password


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
