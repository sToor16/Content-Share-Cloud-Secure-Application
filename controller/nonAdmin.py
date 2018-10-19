from flask import Blueprint, render_template, session, redirect

nonAdmin = Blueprint('nonAdmin', __name__, template_folder='templates')

@nonAdmin.route('/')
@nonAdmin.route('/groups')
def hello_world():
    if 'isAdmin' in session:
        return "Bad Page"
    if 'isActive' in session:
        return render_template('nonAdmin/groups.html')
    else:
        return redirect('login')