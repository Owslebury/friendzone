from flask import Blueprint, Flask, render_template, request, session, g, redirect
from helpers import login_required, read_file_lines
from cs50 import SQL

app = Flask(__name__)
find_bp = Blueprint('about', __name__)
db = SQL("sqlite:///users.db")

def handle_selection(data_type, data_list_key, data_table, data_column):
    data = read_file_lines(data_list_key)

    if request.method == "GET":
        currently_selected = db.execute(f"SELECT {data_column} FROM {data_table} WHERE userid = ?", (session["user_id"],))
        return render_template(f"{data_type}.html", data=data, currently_selected=currently_selected)
    else:
        data = [item.strip() for item in data]
        selected_items = request.form.getlist('selected-items')
        selected_items = [item for item in selected_items if item.strip()]
        selected_items = [item.strip() for item in selected_items]

        db.execute(f"DELETE FROM {data_table} WHERE userid = ?", session["user_id"])
        for item in selected_items:
            if item in data:
                db.execute(f"INSERT INTO {data_table} (userid, {data_column}) VALUES (?, ?)", session["user_id"], item)

        #result = db.execute(f"SELECT {data_column} FROM {data_table} WHERE userid = ?", (session["user_id"],))
        #for row in result:
            #print(row[data_column])

        if selected_items:
            #return f"Selected {data_type}: " + ', '.join(selected_items)
            return redirect("/find")
        else:
            
            return render_template(f"{data_type}.html", result=f"You must choose at least one {data_column}", data=data)


@find_bp.route('/find', methods=["GET", "POST"])
@login_required
def find():
    if request.method == "GET":
        languages = db.execute(f"SELECT language FROM languages WHERE userid = ?",session["user_id"])
        if languages == []:
            return redirect("/find/1")
        locations = db.execute(f"SELECT country FROM locations WHERE userid = ?", session["user_id"])
        if locations == []:
            return redirect("/find/2")

        languages = listWithCommas(languages,'language')
        locations = listWithCommas(locations,'country')

        users = db.execute("SELECT DISTINCT u.id, u.first_name, up.profile_picture_filename, u.username, up.user_description FROM locations AS l JOIN users AS u ON l.userid = u.id LEFT JOIN UserProfile AS up ON u.id = up.user_id WHERE l.country IN (SELECT country FROM locations WHERE userid = ?) AND l.userid != ?", session["user_id"], session["user_id"])
        print(users)
        return render_template("find.html",potentialFriends = users, locations = locations, languages = languages)
    else:
        if 'changeLanguages' in request.form:
            db.execute("DELETE FROM languages WHERE userid = ?", session["user_id"])
            return redirect("/find")
        if 'changeCountries' in request.form:
            db.execute("DELETE FROM locations WHERE userid = ?", session["user_id"])
            return redirect("/find")

def listWithCommas(items, parameterName):
    itemsWithCommas = ""
    for i in range(0,len(items) - 1):
        itemsWithCommas +=  items[i][parameterName].replace('_',' ') + ", "
    itemsWithCommas += items[len(items) - 1][parameterName].replace('_',' ')
    return itemsWithCommas

@find_bp.route('/find/1', methods=["GET", "POST"])
@login_required
def find1():

    #return handle_selection("find2", "data\countries.txt", "countries", "country")
    return handle_selection("find1", "data\languages.txt", "languages", "language")

@find_bp.route('/find/2', methods=["GET", "POST"])
@login_required
def find2():
    #return render_template("find2.html", countries = read_file_lines("data\countries.txt"))
    return handle_selection("find2", "data\countries.txt", "locations", "country")

app.register_blueprint(find_bp)
