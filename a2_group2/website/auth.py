from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

# Create a blueprint - make sure all BPs have unique names
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # NOTE: While the login page uses hardcoded JS auth, this route just renders the template.
    # When real backend auth is ready: uncomment the LoginForm block below and remove the JS
    # hardcoded check in login.html (see the TODO comment there).

    # -- Uncomment this block when switching to real Flask-Login auth --
    # login_form = LoginForm()
    # error = None
    # if login_form.validate_on_submit():
    #     user_name = login_form.user_name.data
    #     password = login_form.password.data
    #     user = db.session.scalar(db.select(User).where(User.name == user_name))
    #     if user is None:
    #         error = 'Incorrect user name'
    #     elif not check_password_hash(user.password_hash, password):
    #         error = 'Incorrect password'
    #     if error is None:
    #         login_user(user)
    #         nextp = request.args.get('next')
    #         if nextp is None or not nextp.startswith('/'):  # BUG FIX: was 'next is None'
    #             return redirect(url_for('main.index'))
    #         return redirect(nextp)
    #     else:
    #         flash(error)
    # return render_template('login.html', form=login_form)

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Stub — register page template to be built separately
    register_form = RegisterForm()
    return render_template('user.html', form=register_form, heading='Register')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
