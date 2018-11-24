from flask import Blueprint, render_template, session, redirect, request
from controller.externalAccess import establishConnection

adminGroup = Blueprint('adminGroup', __name__, template_folder='templates')

@adminGroup.route('/admin/groups')
def adminGroups():
    if 'isAdmin' in session:
        try:
            connection = establishConnection()
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
            connection.close()
        return render_template('admin/groups.html', groups = result, acceptRequests = acceptRequests);
    else:
        return "NO ACCESS SORRY"

@adminGroup.route('/admin/deleteGroup', methods = ['GET', 'POST'])
def deleteGroup():
    idgroup = request.form['deleteGroupID']
    try:
        connection = establishConnection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM groups WHERE idgroup=%s"
            cursor.execute(sql, (idgroup))
            connection.commit()
    finally:
        connection.close()

    return redirect('/admin/groups')

@adminGroup.route('/admin/activateGroup', methods=['GET', 'POST'])
def activateGroup():
    idgroup = request.form['activateGroupID']
    groupOwner = request.form['groupOwner']

    print("idgroup: " + idgroup)
    print("groupOwner: " + groupOwner)
    try:
        connection = establishConnection()

        with connection.cursor() as cursor:
            sql = "UPDATE `groups` SET isActive = '%s' WHERE idgroup=%s"
            cursor.execute(sql, (1, idgroup))
            connection.commit()

            sql = "INSERT INTO group_members (idgroup, member, accepted) VALUES (%s,%s,%s)"
            cursor.execute(sql,(idgroup,groupOwner,1))
            connection.commit()
    finally:
        connection.close()
    return redirect('/admin/groups')

@adminGroup.route('/admin/acceptGroupJoin', methods=['GET','POST'])
def acceptGroupJoin():
    idRequest = request.form['requestID']

    try:
        connection = establishConnection()

        with connection.cursor() as cursor:
            sql = "UPDATE group_members SET accepted = '%s' " \
                  "WHERE id = %s"
            cursor.execute(sql, (1, idRequest))
            connection.commit()
    finally:
        connection.close()

    return redirect('/admin/groups')