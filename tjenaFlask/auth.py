#blueprint for authentication functions
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from tjenaFlask.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST')) #register VIEW
def register(): 
    if request.method == 'POST': #if user submits form
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",  #sql query with ? placeholder, and tuple to replace placeholder with
                    (username, generate_password_hash(password)), #password is hashed before storing in db
                )
                db.commit() #query modifies data, so db.commit is called
            except db.IntegrityError: 
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login")) #generates url for login view based on its name

        flash(error) #flash stores messages that can be retrieved when rendering the template

    return render_template('auth/register.html') #HTML with register form should be shown

@bp.route('/login', methods=('GET', 'POST')) #login VIEW
def login(): 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone() #returns one row from query

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):  #hashes the submitted password in the same way as the stored hash and securely compares them.
            error = 'Incorrect password.'

        if error is None:
            session.clear()  #session = dict that stores data across requests. After successful validation, user id is stored in a new session, 
            session['user_id'] = user['id'] 
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

'''This decorator returns a new view function that wraps the original view it’s applied to. 
The new function checks if a user is loaded and redirects to the login page otherwise. 
If a user is loaded the original view is called and continues normally.
'''
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view