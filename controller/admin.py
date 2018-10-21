from flask import Blueprint, render_template, session, redirect, request
from controller import connection

admin = Blueprint('admin', __name__, template_folder='templates')

@admin.route('/admin/users')
def adminUsers():
    if 'isAdmin' in session:
        try:
            with connection.cursor() as cursor:
                isAdmin = 0;
                sql = "SELECT userID, name, isActive FROM `Users` WHERE isAdmin=%s"

                cursor.execute(sql, (isAdmin))
                result = cursor.fetchall()
        finally:
            print("connection closed commented")
            # connection.close()
        return render_template('admin/users.html', users = result);
    else:
        return "NO ACCESS SORRY"

@admin.route('/admin/groups')
def adminGroups():
    if 'isAdmin' in session:
        try:
            with connection.cursor() as cursor:
                isAdmin = 0;
                sql = "SELECT * FROM `groups`"
                cursor.execute(sql)
                result = cursor.fetchall()

                sql = "SELECT groups.idgroup, groups.name, group_members.member, group_members.id " \
                      "FROM group_members " \
                      "INNER JOIN groups ON " \
                      "group_members.idgroup = groups.idgroup " \
                      "WHERE group_members.accepted = %s"
                cursor.execute(sql, (0))
                acceptRequests = cursor.fetchall()
                print(acceptRequests)
        finally:
            print("connection closed commented")
            # connection.close()
        return render_template('admin/groups.html', groups = result, acceptRequests = acceptRequests);
    else:
        return "NO ACCESS SORRY"

@admin.route('/admin/deactivateUser', methods = ['GET','POST'])
def deactivateUser():
    user_id = request.form['deactivateUserID']
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE `Users` SET isActive = '%s' WHERE userID=%s"
            cursor.execute(sql, (0,user_id))
            result = cursor.fetchall()
            connection.commit()
    finally:
        print("connection closed commented")
        # connection.close()
    return redirect('/admin/users')

@admin.route('/admin/activateUser', methods = ['GET','POST'])
def activateUser():
    user_id = request.form['activateUserID']
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE `Users` SET isActive = '%s' WHERE userID=%s"
            cursor.execute(sql, (1,user_id))
            result = cursor.fetchall()
            connection.commit()
    finally:
        print("connection closed commented")
        # connection.close()
    return redirect('/admin/users')

@admin.route('/admin/deactivateGroup', methods = ['GET', 'POST'])
def deactivateGroup():
    idgroup = request.form['deactivateGroupID']
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE `groups` SET isActive = '%s' WHERE idgroup=%s"
            cursor.execute(sql, (0, idgroup))
            result = cursor.fetchall()
            connection.commit()
    finally:
        print("connection closed commented")
        # connection.close()

    return redirect('/admin/groups')


@admin.route('/admin/activateGroup', methods=['GET', 'POST'])
def activateGroup():
    idgroup = request.form['activateGroupID']
    groupOwner = request.form['groupOwner']

    print("idgroup: " + idgroup)
    print("groupOwner: " + groupOwner)
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE `groups` SET isActive = '%s' WHERE idgroup=%s"
            cursor.execute(sql, (1, idgroup))
            connection.commit()

            sql = "INSERT INTO group_members (idgroup, member, accepted) VALUES (%s,%s,%s)"
            cursor.execute(sql,(idgroup,groupOwner,1))
            connection.commit()
    finally:
        print("connection closed commented")
    return redirect('/admin/groups')

@admin.route('/admin/acceptGroupJoin', methods=['GET','POST'])
def acceptGroupJoin():
    idRequest = request.form['requestID']

    try:
        with connection.cursor() as cursor:
            sql = "UPDATE group_members SET accepted = '%s' " \
                  "WHERE id = %s"
            cursor.execute(sql, (1, idRequest))
            connection.commit()
    finally:
        print("connection closed commented")

    return redirect('/admin/groups')
