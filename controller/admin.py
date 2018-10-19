from flask import Blueprint, render_template, session
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
        return render_template('admin/groups.html');
    else:
        return "NO ACCESS SORRY"