from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_wtf.csrf import generate_csrf
from flask_login import login_required, current_user
from .forms import EditProfileForm, EventForm
from .models import Event, Comment, Order, Event
from . import db
import os
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/category/<category>')
def index(category=None):
    if category:
        events = Event.query.filter_by(category=category).all()
    else:
        events = Event.query.all()
    return render_template('events/index.html', events=events, current_category=category)

@main_bp.route('/user/profile')
@login_required
def profile():
    hosted_events = Event.query.filter_by(user_id=current_user.id).all()
    orders = Order.query.filter_by(user_id=current_user.id).all()
    comments = Comment.query.filter_by(user_id=current_user.id).all()
    
    now = datetime.now()
    upcoming_events = Event.query.filter(
        Event.user_id == current_user.id,
        Event.date >= now
    ).all()
    
    past_events = Event.query.filter(
        Event.user_id == current_user.id,
        Event.date < now
    ).all()
    
    return render_template('user/profile.html', 
                           user=current_user, 
                           hosted_events=hosted_events, 
                           orders=orders,
                           upcoming_events=upcoming_events,
                           past_events=past_events,
                           comments=comments)

@main_bp.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        print("FROM SUBMITTED")
        print("PROFILE IMAGE DATA:", form.profile_image.data)

        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.bio = form.bio.data
        current_user.language = form.languages.data
        current_user.cultural_interests = form.cultural_interests.data

        if form.profile_image.data:
            print("IMAGE FOUND")

            image_file = form.profile_image.data
            filename = secure_filename(image_file.filename)

            upload_folder = os.path.join(
                current_app.root_path,
                'static',
                'profile_pics'
            )

            os.makedirs(upload_folder, exist_ok=True)

            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)

            current_user.profile_image = filename

        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('main.profile'))
    return render_template('user/edit_profile.html', form=form, user=current_user)

@main_bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)

            # Build absolute path so it works on any OS
            images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
            os.makedirs(images_dir, exist_ok=True)  # Create folder if it doesn't exist
            image_file.save(os.path.join(images_dir, image_filename))

        # Create new event
        event = Event(
            name=form.name.data,
            category=form.category.data,
            date=form.date.data,
            location=form.location.data,
            description=form.description.data,
            image=image_filename,
            tickets_available=form.tickets_available.data,
            price=form.price.data,
            acknowledgement=form.acknowledgement.data,
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!')
        return redirect(url_for('main.index'))

    return render_template('events/create.html', form=form)

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = db.session.get(Event, event_id)
    return render_template('events/detail.html', event=event, csrf_token=generate_csrf())

@main_bp.route('/event/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty.')
        return redirect(url_for('main.event_detail', event_id=event_id))

    comment = Comment(
        content=content,
        user_id=current_user.id,
        event_id=event_id
    )
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.event_detail', event_id=event_id) + '#comments')

@main_bp.route('/acknowledgement')
def acknowledgement():
    return render_template('events/acknowledgement.html')