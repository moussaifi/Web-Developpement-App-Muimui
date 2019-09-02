from flask import (Blueprint, render_template, redirect, url_for,
                   abort, flash)
from flask.ext.login import login_user, logout_user, login_required
from itsdangerous import URLSafeTimedSerializer
from app import app, models, db
from app.forms import user as user_forms
from app.toolbox import email

# Serializer for generating random tokens
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create a user blueprint
userbp = Blueprint('userbp', __name__, url_prefix='/user')


@userbp.route('/signup', methods=['GET', 'POST'])
def signup():
    ''' Render signup for to register user
    and insert entry in database '''
    form = user_forms.SignUp()
    mapping = {q.user_name: int(q.id)
               for q in models.InstaInfluencer.query.with_entities(
                                    models.InstaInfluencer.user_name,
                                    models.InstaInfluencer.id).distinct()}
    form.insta_influencers.choices = [(k, k) for k, v in mapping.items()]
    if form.validate_on_submit():
        # Create a user who hasn't validated his email address
        user = models.User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            email=form.email.data,
            confirmation=False,
            _password=form.password.data,
        )

        # Insert the user in the database
        db.session.add(user)
        db.session.commit()
        for ids in form.insta_influencers.data:
            if_id = mapping[ids]
            insta_map = models.UserInfluencerMap(
                user_email=form.email.data,
                influencer_id=int(if_id))
            db.session.add(insta_map)
        db.session.commit()
        # Subject of the confirmation email
        # subject = 'Please confirm your email address.'
        # Generate a random token
        # token = ts.dumps(user.email, salt='email-confirm-key')
        # Build a confirm link with token
        # confirmUrl = url_for('userbp.confirm', token=token, _external=True)
        # Render an HTML template to send by email
        # html = render_template('email/confirm.html',
        #                       confirm_url=confirmUrl)
        # Send the email to user
        # email.send(user.email, subject, html)
        # Send back to the home page
        # flash('Check your emails to confirm your email address.', 'positive')
        return redirect(url_for('product'))
    return render_template('user/signup2.html', form=form, title='Sign up')


@userbp.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm(token):
    ''' Return email confirmation and redirect user to sign-in '''
    try:
        email = ts.loads(token, salt='email-confirm-key', max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)

    # Get the user from the database
    user = models.User.query.filter_by(email=email).first()
    # The user has confirmed his or her email address
    user.confirmation = True
    # Update the database with the user
    db.session.commit()
    # Send to the signin page
    flash(
        'Your email address has been confirmed, you can sign in.', 'positive')
    return redirect(url_for('userbp.signin'))


@userbp.route('/signin', methods=['GET', 'POST'])
def signin():
    ''' Function to direct user to index page if log-in is successful,
    back to sign in page if incorrect password/email is given
    '''
    form = user_forms.Login()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        # Check the user exists
        if user is not None:
            # Check the password is correct
            if user.check_password(form.password.data):
                login_user(user)
                # Send back to the home page
                flash('Succesfully signed in.', 'positive')
                return redirect(url_for('product'))
            else:
                flash('The password you have entered is wrong.', 'negative')
                return redirect(url_for('userbp.signin'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.signin'))
    return render_template('user/signin2.html', form=form, title='Sign in')


@userbp.route('/signout')
@login_required
def signout():
    ''' Function to signout user
    and redirect to index page '''
    logout_user()
    flash('Succesfully signed out.', 'positive')
    return redirect(url_for('index'))


@userbp.route('/account')
@login_required
def account():
    ''' Render page for user account details '''
    return render_template('user/account.html', title='Account')


@userbp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    ''' Functions to handle cases when user forgets email id
    Redirect user to index page after '''
    form = user_forms.Forgot()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        # Check the user exists
        if user is not None:
            # Subject of the confirmation email
            subject = 'Reset your password.'
            # Generate a random token
            token = ts.dumps(user.email, salt='password-reset-key')
            # Build a reset link with token
            resetUrl = url_for('userbp.reset', token=token, _external=True)
            # Render an HTML template to send by email
            html = render_template('email/reset.html', reset_url=resetUrl)
            # Send the email to user
            email.send(user.email, subject, html)
            # Send back to the home page
            flash('Check your emails to reset your password.', 'positive')
            return redirect(url_for('index'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.forgot'))
    return render_template('user/forgot.html', form=form)


@userbp.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    ''' Functions to handle reset settings for password change '''
    try:
        email = ts.loads(token, salt='password-reset-key', max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)
    form = user_forms.Reset()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=email).first()
        # Check the user exists
        if user is not None:
            user.password = form.password.data
            # Update the database with the user
            db.session.commit()
            # Send to the signin page
            flash('Your password has been reset, you can sign in.', 'positive')
            return redirect(url_for('userbp.signin'))
        else:
            flash('Unknown email address.', 'negative')
            return redirect(url_for('userbp.forgot'))
    return render_template('user/reset.html', form=form, token=token)
