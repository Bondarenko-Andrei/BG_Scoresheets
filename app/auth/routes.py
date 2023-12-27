from flask import render_template, url_for, redirect, session, flash
from flask_login import login_user, login_required, current_user, logout_user
from app import db
from app.auth import bp_auth
from app.auth.forms import LoginForm, RegisterForm, ChangePasswordRequestForm, ChangePasswordForm, EditUserForm
from app.models import User


@bp_auth.route("/register", methods=("GET", "POST"))
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data,
                        email=form.email.data,
                        bgg_username=form.bgg_username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f"You have successfully registered! Thank you, {new_user.username}!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@bp_auth.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(username=form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username and/or password, please try again!", "warning")
            return redirect(url_for("auth.login"))
        login_user(user)
        flash(f"You have successfully logged in! Hello, {user.username}!", "success")
        return redirect(url_for("profile.profile"))

    return render_template("login.html", form=form)


@bp_auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("index"))


@bp_auth.route("/change_password_request", methods=("GET", "POST"))
def change_password_request():
    form = ChangePasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
        if user is None:
            flash("User with indicated email not found. Please check input data and try again!", "warning")
            return redirect(url_for("auth.change_password_request"))
        session["user_id"] = user.id
        return redirect(url_for("auth.change_password"))
    return render_template("change_password_request.html", form=form)


@bp_auth.route("/change_password", methods=("GET", "POST"))
def change_password():
    if current_user.is_authenticated:
        user = current_user
    else:
        user = db.session.get(User, session["user_id"])
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password was successfully changed!", "success")
        if current_user.is_authenticated:
            return redirect(url_for("profile.profile"))
        else:
            return redirect(url_for("auth.login"))
    return render_template("change_password.html", form=form)


@bp_auth.route("/edit_profile", methods=("GET", "POST"))
@login_required
def edit_profile():
    user = current_user
    form = EditUserForm(user.username, user.email, obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.bgg_username = form.bgg_username.data
        db.session.commit()
        flash("Your changes have been saved!", "success")
        return redirect(url_for("profile.profile"))
    return render_template("edit_profile.html", form=form)
