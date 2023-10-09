from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User, Feedback
from forms import UserForm, FeedbackForm, DeleteForm
""" from flask_debugtoolbar import DebugToolbarExtension """
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flaskfeedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "shhhhhsecret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

with app.app_context():
    db.create_all()

app.app_context().push()
""" toolbar = DebugToolbarExtension(app) """

@app.route('/')
def home_page():

    form = UserForm()

    return render_template('index.html', form=form)


@app.route('/register', methods = ["GET", "POST"])
def show_form():
    """ Show registration form and authenticate it. """

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username is already taken, please try again.")

            return redirect('/register')
        
        session['username'] = new_user.username

        return redirect(f'/users/{session["username"]}')
    else:
        return render_template('register.html', form=form)



@app.route('/login', methods =["GET", "POST"])
def login_form():
    """ Show and handle a login form. """

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        
        if user:
            session['username'] = user.username

            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Bad name / password']
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/users/<username>')
def secret_route(username):
    """ Show secret route or redirect to home page if not logged in."""

    if "username" not in session:
        flash("You must be logged in to view this page.")

        return redirect('/')
    else:
        user = User.query.get(username)
        form = DeleteForm()
        print("***************")      
        flash('You made it!')

        return render_template('secret.html', user=user, form=form)


@app.route('/logout')
def logout_user():
    """ Log out user and remove user_id from session."""

    session.pop('username')

    return redirect('/')


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """ Delete a user. """

    if "username" not in session:
        flash('Must be logged in to use this function.')

        return redirect('/')
    
    else:
        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('username')

        return redirect('/login')



@app.route('/users/<username>/feedback', methods=["GET","POST"])
def add_feedback_form(username):
    """ Add feedback form. """

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        print(feedback)
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(feedback)

        return redirect(f'/users/{feedback.username}')
        
    else:
        return render_template('feedback.html',form=form)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """ Delete feedback. """

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        return redirect('/')
    
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f'/users/{feedback.username}')


@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if "username" not in session:

        return redirect('/')

    else:
        form = FeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()

            return redirect(f'/users/{feedback.username}')

        return render_template('edit.html', form=form, feedback=feedback)