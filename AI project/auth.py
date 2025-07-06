from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import db, User

# Defines the auth blueprint, which will group authentication-related routes (e.g., /register, /login, etc.).

bp = Blueprint('auth', __name__)

# GET: renders the registration form.
#
# POST: processes form input:
# Checks if username already exists. If not, creates a new user and saves it to the database. Logs the user in and redirects them to the prediction page.

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        if User.query.filter_by(username=u).first():
            flash('اسم المستخدم موجود')
        else:
            user = User(username=u)
            user.set_password(p)
            db.session.add(user)
            db.session.commit()
            flash('تم التسجيل')
            login_user(user)
            return redirect(url_for('auth.predict'))
    return render_template('register.html')

# Verifies username and password.If correct, logs the user in.Otherwise, flashes an error message.

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['username']).first()
        if u and u.check_password(request.form['password']):
            login_user(u)
            return redirect(url_for('auth.predict'))
        flash('بيانات غير صحيحة')
    return render_template('login.html')

# Ensures only authenticated users can access this route.

@bp.route('/predict', methods=['GET'])
@login_required
def predict():
    return render_template('predict.html')

# logout_user() (from Flask‑Login) clears the current user's session. This means:
# The user's session cookie is removed. current_user.is_authenticated becomes False for future requests.

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# When a user logs in, Flask‑Login stores their user.get_id() in the session.

def load_user(user_id):
    return User.query.get(int(user_id))