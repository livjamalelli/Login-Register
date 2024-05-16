from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import md5, re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'SuperSecretKey'
mysql = MySQLConnector(app,'usersdb')


@app.route('/')
def index():
    return render_template('index.html') # pass data to our template


@app.route('/success')
def success():
    # Get user id from session
    id = session['user_id']
    # Get user info by id from database
    query = "SELECT * FROM users WHERE id = {}".format(id)       
    data = mysql.query_db(query) 
    return render_template('success.html', user_info=data)


@app.route('/process', methods=['POST'])
def process():
    is_valid = True
    ftype = request.form['type']
    # Registration form
    if (ftype == 'register'):
        # Validations:
        # 1. First Name - letters only, at least 2 character
        # 2. Last Name - letters only, at least 2 character
        # 3. Email - Valid Email format
        # 4. Password - at least 8 characters
        # 5. Password Confirmation - matches password
        fname = request.form['first_name']
        lname = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        password_confirmation = request.form['password_confirmation']
        if len(email) < 1:
            flash("Email cannot be empty!")
            is_valid = False
        elif not EMAIL_REGEX.match(request.form['email']):
            flash("Invalid Email Address!")
            is_valid = False
        if len(fname) < 2:
            flash("First Name must be at least 2 characters.")
            is_valid = False
        if not fname.isalpha():
            flash("First Name must be letters only.")
            is_valid = False
        if len(lname) < 2:
            flash("Last Name must be at least 2 characters.")
            is_valid = False
        if not lname.isalpha():
            flash("Last Name must be letters only.")
            is_valid = False
        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            is_valid = False
        if password != password_confirmation:
            flash("Password Confirmation must match Password.")
            is_valid = False

        # If the data is valid, we insert new user into the table    
        if (is_valid):
            # Insert into the table
            query = "INSERT INTO users (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)"
            # encrypt the password we provided as 32 character string
            hashed_password = md5.new(password).hexdigest()
            data = {
                'first_name': fname,
                'last_name': lname,
                'email': email,
                'password': hashed_password
            }
            result = mysql.query_db(query, data)
            session['user_id'] = result # TODO: get row id from query result;
            return redirect('/success')

    # Login form
    elif (ftype == 'login'):
        email = request.form['login_email']
        password = request.form['login_password']

        # Validate that the email field is not empty.
        if len(email) < 1:
            flash("Email cannot be empty!")
            is_valid = False 
        elif not EMAIL_REGEX.match(email):
            flash("Invalid Email Address!")
            is_valid = False

        # Check that the user is registered.
        query = "SELECT * FROM users WHERE email = '{}'".format(email)
        data = mysql.query_db(query)
        if (len(data) < 1):
            flash("Email does not exist. Register first!")
            is_valid = False
        # Make sure the password matches
        elif (data[0]['password'] != md5.new(password).hexdigest()):
            flash("Incorrect password. Try again!")
            is_valid = False
        
        if (is_valid):
            session['user_id'] = data[0]['id']
            return redirect('/success')

    return redirect('/')


app.run(debug=True)