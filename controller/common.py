from flask import Blueprint, render_template, request, redirect, session, flash
from controller import bcrypt
import re
import datetime
from controller.externalAccess import establishConnection, upload_blob, download_blob

common = Blueprint('common', __name__, template_folder='templates')

@common.route('/')
@common.route('/login', methods=['GET', 'POST'])
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

@common.route('/register', methods=["GET","POST"])
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

@common.route('/logout', methods=['GET'])
def logout():
    session.pop('isActive',None)
    session.pop('isAdmin',None)
    session.pop('name',None)

    return redirect('/login')

@common.route('/selectedGroup', methods=['GET','POST'])
def selectedGroup():

    idgroup = request.form['idgroup']

    try:
        connection = establishConnection()
        with connection.cursor() as cursor:

            sql = "SELECT groups.*, group_items.* FROM groups " \
                  "LEFT JOIN group_items " \
                  "ON groups.idgroup = group_items.idgroup " \
                  "WHERE groups.idgroup = %s"
            cursor.execute(sql,(idgroup))
            result = cursor.fetchall();

            print(result)

    finally:
        print("connection closed");
        # connection.close()

    return render_template('common/selected_group.html', groupData = result);

@common.route('/uploadNewFile', methods=['POST'])
def uploadPage():
    idgroup = request.form['idgroup']
    return render_template('common/upload_file.html', idgroup = idgroup)

@common.route('/uploadFile', methods=['POST'])
def uploadFile():
    idgroup = request.form['idgroup']
    description = request.form['description']
    name = request.form['name']

    file = request.files.get('file')

    bucket_name = 'secure-flask-app-bucket'
    destination_blob_name = idgroup + "/" + file.filename
    upload_blob(bucket_name, file, destination_blob_name)

    now = datetime.datetime.now()
    time = now.time()
    date = now.date()
    bucket_base = 'https://storage.googleapis.com/secure-flask-app-bucket/'
    full_file_url = bucket_base + destination_blob_name

    try:
        connection = establishConnection()
        with connection.cursor() as cursor:

            sql = "INSERT INTO group_items " \
                  "(idgroup, file_url, uploader_id, name, description, " \
                  "date, time, date_access, time_access) " \
                  "VALUES " \
                  "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (idgroup, full_file_url, session['userID'], name,
                                 description, date, time, date, time))


        connection.commit()
    finally:
        connection.close()

    return "success"

@common.route('/downloadFile', methods=['POST'])
def downloadFile():
    idgroup_items = request.form['idgroup_items']

    now = datetime.datetime.now()
    time = now.time()
    date = now.date()

    bucket_name = 'secure-flask-app-bucket'

    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "UPDATE group_items SET " \
                  "date_access= %s, time_access = %s " \
                  "WHERE idgroup_items = %s"
            cursor.execute(sql,(date, time, idgroup_items))
        connection.commit()

    finally:
        connection.close()

    return "success"
