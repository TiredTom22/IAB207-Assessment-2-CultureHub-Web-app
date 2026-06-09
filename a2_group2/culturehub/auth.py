from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        # Look up user by email
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is None:
            flash('No account found with that email address.')
        elif not check_password_hash(user.password_hash, password):
            flash('Incorrect password.')
        else:
            login_user(user)
            nextp = request.args.get('next')
            if nextp is None or not nextp.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(nextp)
    return render_template('auth/login.html', form=login_form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        # Check if email already registered
        existing_email = db.session.scalar(db.select(User).where(User.email == register_form.email.data))
        if existing_email:
            flash('An account with that email already exists.')
            return render_template('auth/register.html', form=register_form)

        # Combine first and last name as the display name
        full_name = register_form.first_name.data.strip() + ' ' + register_form.last_name.data.strip()

        # Check if this full name is already taken
        existing_name = db.session.scalar(db.select(User).where(User.name == full_name))
        if existing_name:
            flash('An account with that name already exists. Please contact support.')
            return render_template('auth/register.html', form=register_form)

        # Create and save new user
        new_user = User(
            name=full_name,
            email=register_form.email.data,
            phone=register_form.phone.data,
            address=register_form.address.data,
            password_hash=generate_password_hash(register_form.password.data).decode('utf-8')
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=register_form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
