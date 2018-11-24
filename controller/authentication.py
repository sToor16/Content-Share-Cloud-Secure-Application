from flask import Blueprint, render_template, session, redirect, request, flash
from controller.externalAccess import establishConnection

from controller import bcrypt
import re

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

    if request.method == "POST":
        userName = request.form['user_name']
        user_id = request.form['user_id']
        password = request.form['password']


        if len(userName) == 0:
            flash("Please enter username")
            return render_template('common/register.html')
        elif len(userName) > 80:
            flash("Username to long")
            return render_template('common/register.html')

        if len(user_id) == 0:
            flash("Please enter userid")
            return render_template('common/register.html')
        elif len(user_id) > 16:
            flash("user id too long")
            return render_template('common/register.html')

        if not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            flash("Password must contain Uppercase, lowercase, digit and special "
                  "character and should be atleast 8 characters long")
            return render_template('common/register.html')


        hashedPw = bcrypt.generate_password_hash(password)

        connection = establishConnection()

        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `Users` (`name`, `userID`, `password`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (userName, user_id,hashedPw))
            connection.commit()
        finally:
            connection.close()

    return render_template('common/register.html');

@authentication.route('/logout', methods=['GET'])
def logout():
    session.pop('isActive',None)
    session.pop('isAdmin',None)
    session.pop('name',None)

    return redirect('/login')