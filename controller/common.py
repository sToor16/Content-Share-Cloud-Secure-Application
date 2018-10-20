from flask import Blueprint, render_template, request, redirect, session
from controller import connection, bcrypt

common = Blueprint('common', __name__, template_folder='templates')

@common.route('/register', methods=["GET","POST"])
def register():

    if request.method == "POST":
        userName = request.form['user_name']
        user_id = request.form['user_id']
        password = request.form['password']

        hashedPw = bcrypt.generate_password_hash(password)

        try:
            with connection.cursor() as cursor:

                sql = "INSERT INTO `Users` (`name`, `userID`, `password`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (userName, user_id, hashedPw))

            connection.commit()
        finally:
            print("connection closed");
            # connection.close()

    return render_template('common/register.html', title='register');

@common.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        try:
            with connection.cursor() as cursor:

                sql = "SELECT password, isAdmin, isActive FROM `Users` WHERE userID=%s"

                cursor.execute(sql, (user_id))
                result = cursor.fetchall()

                if (len(result) == 0):
                    print("email does not exist")
                else:
                    hasPw = result[0]['password']
                    if bcrypt.check_password_hash(hasPw, password):
                        if result[0]['isActive'] == 1:
                            session['userID'] = user_id
                            session['isActive'] = 'true'
                            if result[0]['isAdmin'] == 1:
                                session['isAdmin'] = 'true'
                                return redirect('/admin/users')
                            else:
                                return redirect('groups')
                        else:
                            print("user not active")
                    else:
                        print("wrong credentials")
        finally:
            print("connection closed commented")
            # connection.close()

    return render_template('common/login.html', title='login');

@common.route('/logout', methods=['GET'])
def logout():
    print(session)
    session.pop('isActive',None)
    session.pop('isAdmin',None)
    print(session)

    return redirect('/login')