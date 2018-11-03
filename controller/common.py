from flask import Blueprint, render_template, request, redirect, session
from controller import connection, bcrypt
import datetime

from google.cloud import storage

common = Blueprint('common', __name__, template_folder='templates')

@common.route('/')
def hello_world():
    return "Welcome to my Secure Website"

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
            connection.close()

    return render_template('common/register.html', title='register');

@common.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        try:
            with connection.cursor() as cursor:

                sql = "SELECT * FROM `Users` WHERE userID=%s"

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
                            session['name'] = result[0]['name']
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
    session.pop('name',None)
    print(session)

    return redirect('/login')

@common.route('/selectedGroup', methods=['GET','POST'])
def selectedGroup():

    idgroup = request.form['idgroup']

    try:
        with connection.cursor() as cursor:

            sql = "SELECT groups.owner, groups.name, group_items.* FROM groups " \
                  "INNER JOIN group_items " \
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
        print("connection closed");
        # connection.close()

    return "success"

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(source_file_name)