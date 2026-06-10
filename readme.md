# CultureHub — IAB207 Assessment 2

A Flask web application for discovering, hosting, and booking cultural events across Brisbane and beyond.

## Team

|       Name        | Student Number |
|-------------------|----------------|
| Thompson Tang     |   n11085908    |
| Amogh Purighalla  |   n12217387    |
| Glenda Fulgidezza |   n12241792    |
| Sohee Chung       |   n11863692    |

## Setup

**Requirements:** Python 3.10+

on CMD, go to the root folder of this web application, please install the following:
pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-wtf flask-bootstrap5 reportlab email-validator

Then run:
cd a2_group2
python main.py

And wait for the flask to start.

Then, visit :http://127.0.0.1:5000

The database has sample events, users, bookings, comments (on future events) and ratings (only on past events).



Demo Accounts

Username	            Email	        Password
admin	    admin@culturehub.com	    password
amogh	    amogh@culturehub.com	    qut2026
thompson	thompson@culturehub.com	    qut2026
glenda	    glenda@culturehub.com	    qut2026
sohee	    sohee@culturehub.com	    qut2026
thompson1   tom@mail.com                Chery0202@
tomac	    tom@gmail.com               Thomas@123
proxinator	proxinator@gmail.com        Proxinator@123


Please note that the first 5 accounts (admin, amogh, thompson, glenda and sohee) were created hardcoded initially before we coded in validators, which is why their passwords don't have any safety validation. Since we created events on these accounts, we just kept them in. Please do check for validation login by creating a new account.

The last 3 accounts follow validator logic because they were created after we coded in validator checks.


Login accepts either username or email address.

Features:
Browse, search, and filter events by category and status
Register and log in (username or email)
Create, edit, and cancel events
Book tickets with overbooking prevention
Download tickets as PDF
Leave comments on all events and star ratings on past events
User profile with booking history and hosted events
Acknowledgement of Country on event pages
Custom 404 and 500 error pages




