from flask import Blueprint, render_template, session, redirect, request
from controller.externalAccess import establishConnection

adminUser = Blueprint('adminUser', __name__, template_folder='templates')

@adminUser.route('/admin/users')
def adminUsers():
    if 'isAdmin' in session:
        try:
            connection = establishConnection()
            with connection.cursor() as cursor:
                isAdmin = 0;
                sql = "SELECT userID, name, isActive FROM `Users` WHERE isAdmin=%s"

                cursor.execute(sql, (isAdmin))
                result = cursor.fetchall()
        finally:
            connection.close()
        return render_template('admin/users.html', users = result);
    else:
        return "NO ACCESS SORRY"

@adminUser.route('/admin/deleteUser', methods = ['GET','POST'])
def deactivateUser():
    user_id = request.form['deleteUserID']
    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM Users WHERE userID=%s"
            cursor.execute(sql, (user_id))
            result = cursor.fetchall()
            connection.commit()
    finally:
        connection.close()
    return redirect('/admin/users')

@adminUser.route('/admin/activateUser', methods = ['GET','POST'])
def activateUser():
    user_id = request.form['activateUserID']
    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "UPDATE `Users` SET isActive = '%s' WHERE userID=%s"
            cursor.execute(sql, (1,user_id))
            result = cursor.fetchall()
            connection.commit()
    finally:
        connection.close()
    return redirect('/admin/users')
