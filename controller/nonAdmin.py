from flask import Blueprint, render_template, session, redirect, request
from controller.externalAccess import establishConnection

nonAdmin = Blueprint('nonAdmin', __name__, template_folder='templates')

@nonAdmin.route('/groups')
def groups():
    if 'isAdmin' in session:
        return "Bad Page"

    isActive = 1

    if 'isActive' in session:
        try:
            connection = establishConnection()

            with connection.cursor() as cursor:

                sql = "SELECT groups.name, groups.owner, groups.idgroup " \
                      "FROM group_members " \
                      "INNER JOIN groups ON group_members.idgroup = groups.idgroup " \
                      "WHERE group_members.member = %s AND " \
                      "group_members.accepted = %s AND " \
                      "groups.isActive = %s"
                cursor.execute(sql,(session['userID'], 1, 1))
                joined = cursor.fetchall();

                sql = "SELECT groups.idgroup, groups.name, groups.owner FROM groups " \
                      "WHERE groups.isActive = %s AND " \
                      "groups.idgroup NOT IN " \
                      "(" \
                      "SELECT group_members.idgroup FROM group_members " \
                      "WHERE group_members.member = %s" \
                      ")"

                cursor.execute(sql, (1, session['userID']))
                unjoined = cursor.fetchall();

                sql = "SELECT groups.name, groups.idgroup, group_members.member FROM groups " \
                      "LEFT JOIN group_members ON " \
                      "groups.idgroup = group_members.idgroup " \
                      "WHERE (group_members.member = %s AND " \
                      "group_members.accepted = %s) AND" \
                      " groups.isActive = %s"
                cursor.execute(sql, (session['userID'], 0, 1))
                requested = cursor.fetchall();

        finally:
            connection.close()

        return render_template('/nonAdmin/groups.html', joinedGroups = joined, unjoinedGroups = unjoined, requestedGroups = requested)
    else:
        return redirect('login')

@nonAdmin.route('/createGroup', methods=['GET','POST'])
def createGroup():
    name = request.form['name']
    owner = session['userID']

    try:
        connection = establishConnection()
        with connection.cursor() as cursor:

            sql = "INSERT INTO `groups` (`owner`, `name`) VALUES (%s, %s)"
            cursor.execute(sql,(owner, name))
            connection.commit()
    finally:
        connection.close()
    return redirect('/groups')

@nonAdmin.route('/joinGroup', methods=['GET', 'POST'])
def joinGroup():
    idgroup = request.form['groupID']

    try:
        connection = establishConnection()
        with connection.cursor() as cursor:

            sql = "INSERT INTO group_members (idgroup, member)VALUES (%s, %s)"
            cursor.execute(sql,(idgroup, session['userID']))
            connection.commit()
    finally:
        connection.close()

    return redirect('/groups')
