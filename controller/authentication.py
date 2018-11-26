from flask import Blueprint, render_template, session, redirect, request, flash
from controller.externalAccess import establishConnection
from controller.validation import lengthValidation, zeroLengthCheck, passwordRegEx, \
    internationLettersRegEx, englishAlphabetsRegEx

from controller import bcrypt

authentication = Blueprint('authentication', __name__, template_folder='templates')

@authentication.route('/')
@authentication.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        try:
            connection = establishConnection()

            with connection.cursor() as cursor:
                sql = "SELECT * FROM `Users` WHERE userID=%s"
                cursor.execute(sql, (user_id))
                result = cursor.fetchall()
                if (len(result) == 0):
                    flash("userid does not exist")
                    return render_template('common/login.html')
                else:
                    hasPw = result[0]['password']
                    if bcrypt.check_password_hash(hasPw, password):
                        if result[0]['isActive'] == 1:
                            session['userID'] = user_id
                            session['isActive'] = 'true'
                            session['name'] = result[0]['name']
                            if result[0]['isAdmin'] == 1:
                                session['isAdmin'] = 'true'
                                return redirect('/admin/users')
                            else:
                                return redirect('groups')
                        else:
                            flash("You are not yet activated by Admin")
                            return render_template('common/login.html')
                    else:
                        flash("wrong credentials")
                        return render_template('common/login.html')
        finally:
            connection.close()

    return render_template('common/login.html', title='login');

@authentication.route('/register', methods=["GET","POST"])
def register():

    params = {}

    if request.method == "POST":
        params['userName'] = request.form['user_name']
        params['user_id'] = request.form['user_id']
        params['password'] = request.form['password']

        if validation(params):
            if checkIdAvailable(params['user_id']):
                flash("User is already exists")
            else:
                addUser(params)
        else:
            return render_template('common/register.html')
    return render_template('common/register.html')

def validation(params):
    if zeroLengthCheck(params['userName']):
        flash("Please enter your name")
        return 0
    # elif internationLettersRegEx(params['userName']):
    #     flash("Name shoud only have alphabets from international languages and nothing else")
    #     return 0
    elif lengthValidation(params['userName'], 80):
        flash("name to long")
        return 0

    if zeroLengthCheck(params['user_id']):
        flash("Please enter userid")
        return 0
    elif englishAlphabetsRegEx(params['user_id']):
        flash("Only english alphabets allowed in user id")
        return 0
    elif lengthValidation(params['user_id'],16):
        flash("user id too long")
        return 0

    if passwordRegEx(params['password']):
        flash("Password must contain Uppercase, lowercase, digit and special "
              "character and should be atleast 8 characters long")
        return 0
    return 1

def checkIdAvailable(userId):
    connection = establishConnection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM Users " \
                  "WHERE userID = %s"
            cursor.execute(sql, (userId))
            result = cursor.fetchall()
            count = result[0]['COUNT(*)']
            if count == 1:
                return 1
    finally:
        connection.close()

    return 0

def addUser(params):
    hashedPw = bcrypt.generate_password_hash(params['password'])

    connection = establishConnection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Users (name, userID, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (params['userName'], params['user_id'], hashedPw))
        connection.commit()
    finally:
        connection.close()

@authentication.route('/logout', methods=['GET'])
def logout():
    session.pop('isActive',None)
    session.pop('isAdmin',None)
    session.pop('name',None)

    return redirect('/login')