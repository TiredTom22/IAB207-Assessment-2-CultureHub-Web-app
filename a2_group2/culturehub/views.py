from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_wtf.csrf import generate_csrf
from flask_login import login_required, current_user
from .forms import EventForm
from .models import Event, Comment
from . import db
import os
from werkzeug.utils import secure_filename

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
def profile():
    return render_template('user/profile.html')

@main_bp.route('/user/edit-profile')
def edit_profile():
    return render_template('user/edit_profile.html')

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