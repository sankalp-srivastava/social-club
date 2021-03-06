import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(current_app.root_path,'static/profile_pics',picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

    
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                    sender='devatsocialclub@gmail.com',
                    recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for("users.reset_token",token=token,_external=True)}

If you did not sent reset password request then simply ignore this email.
The token is valid for next 30 mins only.

Regards
Developer
Social Club
'''
    mail.send(msg)

def send_email_verification(email,code):
    # token = user.get_reset_token()
    s = Serializer(current_app.config['SECRET_KEY'],900)
    token = s.dumps({'user_code':code}).decode('utf-8')
    msg = Message('Email Verification',
                    sender=os.environ.get('ADMIN_USER_USERNAME'),
                    recipients=[email])
    msg.body = f'''Hello There and Welcome to Social CLub
To verify your email, visit the following link:
{url_for("users.email_verification",token=token,_external=True)}

If you don't remember registering on Social Club then simply ignore this email.
The token is valid for next 15 mins only.

Regards
Developer
Social Club
'''
    mail.send(msg)