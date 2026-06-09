from flask import current_app, Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from .forms import EditProfileForm, EventForm, BookingForm, CreateEventForm
from .models import Event, Comment, Order, User
from . import db
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from werkzeug.utils import secure_filename
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/category/<category>')
def index(category=None):
    # Auto update inactive events
    now = datetime.now()
    past_events = Event.query.filter(Event.date < now, Event.status == 'Open').all()
    for event in past_events:
        event.status = 'Inactive'
    db.session.commit()
    
    search = request.args.get('search')
    if search:
        events = Event.query.filter(Event.name.ilike(f'%{search}%')).all()
    elif category:
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
    
    booked_upcoming = Event.query.join(Order).filter(
        Order.user_id == current_user.id,
        Event.date >= now
    ).all()

    past_orders = [o for o in orders if o.event.date < now]

    return render_template('user/profile.html',
                           user=current_user,
                           hosted_events=hosted_events,
                           orders=orders,
                           past_orders=past_orders,
                           upcoming_events=upcoming_events,
                           past_events=past_events,
                           comments=comments,
                           booked_upcoming=booked_upcoming,
                           saved_events=[])

@main_bp.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        if form.name.data != current_user.name:
            taken = db.session.scalar(db.select(User).where(User.name == form.name.data))
            if taken:
                flash('That username is already taken.')
                return render_template('user/edit_profile.html', form=form, user=current_user)
        if form.email.data != current_user.email:
            taken = db.session.scalar(db.select(User).where(User.email == form.email.data))
            if taken:
                flash('That email address is already linked to another account.')
                return render_template('user/edit_profile.html', form=form, user=current_user)
        current_user.first_name = form.first_name.data.strip()
        current_user.last_name = form.last_name.data.strip()
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.bio = form.bio.data
        current_user.language = form.languages.data
        current_user.cultural_interests = form.cultural_interests.data

        if form.profile_image.data and hasattr(form.profile_image.data, 'filename') and form.profile_image.data.filename != '':
            image_file = form.profile_image.data
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'profile_pics')
            os.makedirs(upload_folder, exist_ok=True)
            image_file.save(os.path.join(upload_folder, filename))
            current_user.profile_image = filename

        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('main.profile'))
    return render_template('user/edit_profile.html', form=form, user=current_user)

@main_bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = CreateEventForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
            os.makedirs(images_dir, exist_ok=True)
            image_file.save(os.path.join(images_dir, image_filename))

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
            acknowledgement_text=form.acknowledgement_text.data,
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!')
        return redirect(url_for('main.index'))

    return render_template('events/create.html', form=form)

@main_bp.route('/acknowledgement')
def acknowledgement():
    return render_template('events/acknowledgement.html')

@main_bp.route('/about')
def about():
    return render_template('user/about-us.html')

@main_bp.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    event = db.session.get(Event, event_id)
    if event is None:
        return render_template('errors/404.html'), 404
    form = BookingForm()
    comments = Comment.query.filter_by(event_id=event_id).all()
    ratings = [c.rating for c in comments if c.rating is not None]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

    if request.method == 'POST':
        comment_text = request.form.get('comment', '').strip()
        if comment_text and current_user.is_authenticated:
            rating_val = request.form.get('rating')
            rating = int(rating_val) if rating_val and rating_val.isdigit() and 1 <= int(rating_val) <= 5 else None
            comment = Comment(
                content=comment_text,
                rating=rating,
                user_id=current_user.id,
                event_id=event_id
            )
            db.session.add(comment)
            db.session.commit()
            flash('Review posted!')
        return redirect(url_for('main.event_detail', event_id=event_id))

    now = datetime.now()
    return render_template('events/event-detail.html', event=event, form=form, comments=comments, avg_rating=avg_rating, now=now)

@main_bp.route('/event/<int:event_id>/book', methods=['POST'])
@login_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        quantity = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        flash('Invalid ticket quantity.')
        return redirect(url_for('main.event_detail', event_id=event_id))
    if quantity < 1:
        flash('Invalid ticket quantity.')
        return redirect(url_for('main.event_detail', event_id=event.id))
    if quantity > event.tickets_available:
        flash('Not enough tickets available.')
        return redirect(url_for('main.event_detail', event_id=event.id))

    order = Order(
        quantity=quantity,
        price=event.price * quantity,
        user_id=current_user.id,
        event_id=event.id
    )

    event.tickets_available -= quantity
    if event.tickets_available == 0:
        event.status = 'Sold Out'
    db.session.add(order)
    db.session.commit()
    
    flash(f'Booking confirmed! Your Order ID is BK-{order.id:06d}')

    return redirect(url_for(
    'main.event_detail',
    event_id=event.id,
    booking='success',
    order_id=order.id
))

@main_bp.route('/event/<int:event_id>/edit' , methods=['GET', 'POST'])
@login_required
def event_edit(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        flash('You do not have permission to edit this event.')
        return redirect(url_for('main.event_detail', event_id=event_id))
    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.name = form.name.data
        event.category = form.category.data
        event.date = form.date.data
        event.location = form.location.data
        event.description = form.description.data
        event.tickets_available = form.tickets_available.data
        event.price = form.price.data
        event.acknowledgement = form.acknowledgement.data
        event.acknowledgement_text = form.acknowledgement_text.data
        
        if event.date > datetime.now():
            event.status = 'Open'
        
        if form.image.data and hasattr(form.image.data, 'filename') and form.image.data.filename != '':
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
            os.makedirs(images_dir, exist_ok=True)
            image_file.save(os.path.join(images_dir, image_filename))
            event.image = image_filename
        db.session.commit()
        flash('Event updated successfully!')
        return redirect(url_for('main.event_detail', event_id=event_id))
    return render_template('events/event_edit.html', form=form, event=event)

@main_bp.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        flash('You are not authorised to cancel this event.')
        return redirect(url_for('main.event_detail', event_id=event_id))
    event.status = 'Cancelled'
    db.session.commit()
    flash('Event has been cancelled.')
    return redirect(url_for('main.event_detail', event_id=event_id))


@main_bp.route('/stories')
def stories():
    return render_template('user/stories.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # No backend processing — acknowledge receipt and redirect
        flash('Thank you for your message! We will get back to you within 2 business days.')
        return redirect(url_for('main.contact'))
    return render_template('user/contact.html')

@main_bp.route('/ticket/<int:order_id>/download')
@login_required
def download_ticket(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        flash("You are not authorised to download this ticket.")
        return redirect(url_for('main.profile'))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.setTitle("CultureHub Ticket")

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(180, 800, "CultureHub Ticket")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(80, 740, f"Booking ID: BK-{order.id:06d}")
    pdf.drawString(80, 710, f"Event: {order.event.name}")
    pdf.drawString(80, 680, f"Hosted by: {order.event.user.name}")
    pdf.drawString(80, 650, f"Date: {order.event.date.strftime('%A, %d %B %Y')}")
    pdf.drawString(80, 620, f"Time: {order.event.date.strftime('%I:%M %p')}")
    pdf.drawString(80, 590, f"Location: {order.event.location}")
    pdf.drawString(80, 560, f"Tickets: {order.quantity}")
    pdf.drawString(80, 530, f"Total Paid: ${order.price:.2f}")

    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(80, 480, "Thank you for booking with CultureHub.")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"CultureHub_Ticket_BK-{order.id:06d}.pdf",
        mimetype='application/pdf'
    )

@main_bp.route('/ticket/<int:order_id>/preview')
@login_required
def preview_ticket(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        flash("You are not authorised to preview this ticket.")
        return redirect(url_for('main.profile'))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.setTitle("CultureHub Ticket Preview")

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(180, 800, "CultureHub Ticket")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(80, 740, f"Booking ID: BK-{order.id:06d}")
    pdf.drawString(80, 710, f"Event: {order.event.name}")
    pdf.drawString(80, 680, f"Hosted by: {order.event.user.name}")
    pdf.drawString(80, 650, f"Date: {order.event.date.strftime('%A, %d %B %Y')}")
    pdf.drawString(80, 620, f"Time: {order.event.date.strftime('%I:%M %p')}")
    pdf.drawString(80, 590, f"Location: {order.event.location}")
    pdf.drawString(80, 560, f"Tickets: {order.quantity}")
    pdf.drawString(80, 530, f"Total Paid: ${order.price:.2f}")

    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(80, 480, "Thank you for booking with CultureHub.")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=False,
        download_name=f"CultureHub_Ticket_BK-{order.id:06d}.pdf",
        mimetype='application/pdf'
    )