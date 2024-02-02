# Friendzone
#### Video Demo:  https://www.youtube.com/watch?v=LGilKCM8KPA
#### Description:
This is a messaging app where you can message people from within user specified languages and countries.

## app.py:
This contains the methods for all of the pages apart from those in find. First the database is connected and the session is configured. The session is not permenant, the session type is filesystem and uploads (e.g. for profile pictures) is set to static/uploads.

### Register
Register has fields GET and POST.
GET returns the page showing fields for first name, last name, username, password and country. 
POST takes these fields and adds them to the database if valid. The password gets hashed by method hashPassword(password). There are lines such as 
```
if not request.form.get("firstName"):
            return redirect("/error")
```
This is because the registration fields should have something in them to allow the user to post, so if they are not there something is wrong with the actual HTML.

### Login
Login has methods GET and POST
GET returns the page showing the username and password sections.
POST takes the username and password, hashes the password and checks the database, allowing the user to sign in if it is contained within the database. It then redirects them to the homepage.

### Error
This method simply returns the error page.

### Profile
Profile has methods GET and POST.
GET returns the page showing input for description, the users current profile picture if they have one and a button to submit to make changes.
POST updates user description and profile picture and returns the same page with them updated.
```
        if file:
            file_extension = os.path.splitext(file.filename)[1]
            filename = os.path.join(app.config['UPLOAD_FOLDER'], str(session["user_id"])+ file_extension)
            file.save(filename)
            db.execute("UPDATE UserProfile SET profile_picture_filename = ? WHERE user_id = ?", filename, session["user_id"])
```
This is the code that saves the file to the uploads folder and then updates the database to include the file directory. 

### Logout
This clears the session and redirects to the homepage.

### Message
This takes the username of the user being messaged in the URL. ``` /message/<username> ``` Message has methods GET and POST. 
GET adds the other user to the list of matches of the user currently signed in. 
POST adds a new message to the database and again returns the messages page.

### HashPassword
Hashes the password using SHA256.

## find.py
### handleSelection
Handles creating the pages with lots of selections. At the moment languages and countries are the only ones that have been added.
GET displays all of the options.
POST deletes the current items of that category (e.g. country or language) and inserts the new ones that have been selected. This means that the user can change their choices of language or country.
If there are selected items redirect to "/find"

### listWithCommas
Puts commas between items in the list

### find/1 and find/2 
These call on handle selection. They represent languages and countries respectively.

## Pages

### Layout
This provides the banner which is shown on all pages with menu items like home, profile, find, sign in, sign up. It also includes bootstrap so that it does not need to be declared explicitly on other sites that it is on.

### Find
The most technically advanced part of my project. This site provides many options for users to select. The search bar works as follows. 
```<script>
        const buttons = document.getElementsByClassName('language-button');
        const searchInput = document.getElementById('search');
        const selectedLanguages = document.getElementById('selected-items');

        searchInput.addEventListener('input', function () {
            const searchTerm = searchInput.value.toLowerCase();

            for (const button of buttons) {
                const buttonText = button.textContent.toLowerCase();

                if (buttonText.includes(searchTerm)) {
                    button.style.display = 'inline-block';
                } else {
                    button.style.display = 'none';
                }
            }
        });
    </script>
```
This script makes it so when something is typed in the search bar it only shows the buttons that match the search time, by displaying them to 'inline-block'.
```
<form method="POST">
        {% for item in data %}
        <button type="button" class="btn btn-light language-button" onclick="toggleLanguage('{{ item }}')">
            {{ item }}
        </button>
        <input type="hidden" id={{ item }} name="selected-items" value="">
        {% endfor %}
        <button class ="btn btn-primary" type="submit">Submit</button>
    </form>
```
When buttons are toggled they are added to the invisible 'selected-items' list which can then be returned to flask. 
```
languageButtons.forEach(function (button) {
            button.addEventListener("click", function () {
                toggleLanguage(button.innerText);
                if (selected.innerText.includes(button.innerText) == false) {
                    languages.push(button.innerText);
                    if (selected.innerText.trim() != "Selected:") {
                        selected.innerText += ", " + button.innerText;
                    }
                    else {
                        selected.innerText += " " + button.innerText;
                    }

                }

            });
        });
```
If the text within the button is not already in selected, push it to the list. If the "Selected:" text does not contain any items append it to the end with a space, otherwise add commas. 

### Message
This page shows all the previous messages between two users.
```
{% for message in messages %}
    {% if message.sender_id == user.id %}
    <div class="message home">
        {{message.message_content}}
    </div>
    {% else %}
    <div class="message away">
        {{message.message_content}}
    </div>
    {% endif %}

    {% endfor %}
```
This puts the messages in blue and white depending on if the message is from or to the user, like in many texting apps.

    
