import json
from app.profile import bp_profile
from flask import render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from app import db
from app.profile.forms import UserPlayersForm, EditFieldsForm, SubmitForm, EditCustomGame
from app.models import Player, Session, Game, Field


@bp_profile.route("/profile")
@login_required
def profile():
    user = current_user
    user.first_session = min(session.session_date for session in user.sessions) if user.sessions else None
    user.last_session = max(session.session_date for session in user.sessions) if user.sessions else None
    return render_template("profile.html", user=user)


@bp_profile.route("/sessions")
@login_required
def sessions():
    edit = False
    sessions = current_user.sessions
    for session in sessions:
        max_result = max([res.result for res in session.results]) if session.results else None
        session.player_names = [player.name for player in session.players]
        session.winners = [f"{res.player.name} ({res.result})" for res in session.results if res.result == max_result]
    return render_template("sessions.html", sessions=sessions, edit=edit)


@bp_profile.route("/edit_sessions", methods=("GET", "POST"))
@login_required
def edit_sessions():
    edit = True
    form = SubmitForm()
    sessions = current_user.sessions
    for session in sessions:
        max_result = max([res.result for res in session.results]) if session.results else None
        session.player_names = [player.name for player in session.players]
        session.winners = [f"{res.player.name} ({res.result})" for res in session.results if res.result == max_result]
    if form.validate_on_submit():
        delete_sessions = request.form.getlist("delete_session")
        for session_id in delete_sessions:
            session = db.session.get(Session, session_id)
            db.session.delete(session)
        db.session.commit()
        return redirect(url_for("profile.sessions"))
    return render_template("sessions.html", sessions=sessions, edit=edit, form=form)


@bp_profile.route("/players", methods=("GET", "POST"))
@login_required
def players():
    edit = False
    players = current_user.players
    for player in players:
        player.first_played = min([session.session_date for session in player.sessions]) if player.sessions else None
        player.last_played = max([session.session_date for session in player.sessions]) if player.sessions else None
    return render_template("players.html", players=players, edit=edit)


@bp_profile.route("/edit_players", methods=("GET", "POST"))
@login_required
def edit_players():
    edit = True

    form = UserPlayersForm()

    players = current_user.players
    for n, player in enumerate(players):
        if request.method == "GET":
            form.players.append_entry(player.name)
        player.edit_name = form.players[n]
        player.first_played = min([session.session_date for session in player.sessions]) if player.sessions else None
        player.last_played = max([session.session_date for session in player.sessions]) if player.sessions else None

    if request.form.get("add_new_player"):
        form.new_players.append_entry()
    elif request.form.get("delete_new_player"):
        if form.new_players.data:
            form.new_players.pop_entry()
    elif form.validate_on_submit():
        delete_players = request.form.getlist("delete_player")
        for player in players:
            player.name = player.edit_name.data
            if str(player.id) in delete_players:
                db.session.delete(player)
                db.session.commit()
        for player in form.new_players:
            new_player = Player(name=player.data, user_id=current_user.id)
            db.session.add(new_player)
        db.session.commit()
        flash("Your changes have been saved!", "success")
        return redirect(url_for("profile.players"))

    return render_template("players.html", players=players, form=form, edit=edit)


@bp_profile.route("/custom_scoresheets")
@login_required
def custom_scoresheets():
    games = current_user.custom_games
    for game in games:
        game_sessions = db.session.scalars(db.select(Session).filter_by(game_id=game.id, user_id=current_user.id)).all()
        game.times_played = len(game_sessions)
    return render_template("custom_scoresheets.html", user=current_user, games=games)


@bp_profile.route("/edit_scoresheet/<int:game_id>", methods=("GET", "POST"))
@login_required
def edit_scoresheet(game_id):
    game = db.session.get(Game, game_id)
    if game not in current_user.custom_games:
        flash("You can edit only YOUR custom scoresheets!", "warning")
        return redirect(url_for("profile.profile"))
    fields = game.fields

    if game.bgg_id:
        form = EditFieldsForm()
    else:
        form = EditCustomGame(data={"name": game.name,
                                    "min_players": game.min_players,
                                    "max_players": game.max_players,
                                    "year": game.year})

    for n, field in enumerate(fields):
        if request.method == "GET":
            form.fields.append_entry(field.name)
        field.edit_name = form.fields[n]

    if request.form.get("add_new_field"):
        form.new_fields.append_entry()
    elif request.form.get("delete_new_field"):
        if form.new_fields.data:
            form.new_fields.pop_entry()
    elif form.validate_on_submit():
        delete_fields = request.form.getlist("delete_field")
        for field in fields:
            field.name = field.edit_name.data
            if str(field.id) in delete_fields:
                db.session.delete(field)
                db.session.commit()
        for field in form.new_fields:
            new_field = Field(name=field.data, game_id=game_id)
            db.session.add(new_field)
        if not game.bgg_id:
            game.name = form.name.data
            game.min_players = form.min_players.data
            game.max_players = form.max_players.data
            game.year = form.year.data
        db.session.commit()
        flash("Your changes have been saved!", "success")
        return redirect(url_for("profile.edit_scoresheet", game_id=game_id))

    return render_template("edit_scoresheet.html",
                           game=game,
                           fields=fields,
                           form=form)


@bp_profile.route("/delete_scoresheet/<int:game_id>")
@login_required
def delete_scoresheet(game_id):
    game = db.session.get(Game, game_id)
    if game not in current_user.custom_games:
        flash("You can delete only YOUR custom scoresheets!", "warning")
        return redirect(url_for("profile.profile"))
    db.session.delete(game)
    db.session.commit()
    flash(f"Your scoresheet for {game.name} has been deleted.", "success")
    return redirect(url_for("profile.custom_scoresheets"))


@bp_profile.route("/session_results/<int:session_id>")
@login_required
def session_results(session_id):
    session = db.session.get(Session, session_id)
    if session not in current_user.sessions:
        flash("You can view only YOUR sessions!", "warning")
        return redirect(url_for("profile.profile"))
    game = session.game
    fields = json.loads(session.field_names)
    results = session.results
    player_results = [
        {"player": res.player.name,
         "field_results": json.loads(res.field_results),
         "result": res.result}
        for res in results
    ]
    return render_template("session_results.html", fields=fields, player_results=player_results,
                           game=game)
