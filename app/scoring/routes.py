import json
from datetime import date
from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user
from wtforms import Form, FieldList, StringField, IntegerField, FormField
from app import db
from app.scoring import bp_game_scoring
from app.models import Game, Player, Session, PlayerResult
from app.scoring.forms import (SelectGameForm,
                               BaseSubmitForm)


@bp_game_scoring.route("/scoring", methods=("GET", "POST"))
def select_game():
    base_games = db.session.scalars(db.select(Game.name).filter_by(user_id=None).order_by(Game.name)).all()
    if current_user.is_authenticated:
        user_games = db.session.scalars(db.select(Game.name).filter_by(user_id=current_user.id).order_by(Game.name)).all()
        games = {"Base games": base_games, "My games": user_games}
    else:
        games = base_games

    form = SelectGameForm()
    form.game_name.choices = games

    if form.validate_on_submit():
        game = db.session.execute(db.select(Game).where(Game.name == form.game_name.data)).scalar()
        return redirect(url_for("scoring.scoring", game_id=game.id))

    return render_template("select_game.html", form=form, game_chosen=False)


@bp_game_scoring.route("/scoring/<int:game_id>", methods=("GET", "POST"))
def scoring(game_id):
    game = db.session.get(Game, game_id)
    if not game.min_players:
        game.min_players = 1
    number_of_players = game.min_players
    fields = [field.name for field in game.fields]
    number_of_fields = len(fields)

    class ScoreFieldsForm(Form):
        pass

    for n, field in enumerate(fields):
        setattr(ScoreFieldsForm,
                f"score_field_{n + 1}",
                FieldList(IntegerField(), label=field, min_entries=number_of_players))

    class ScoreForm(BaseSubmitForm):
        players = FieldList(StringField("Player"), "Players", min_entries=number_of_players)
        scores = FormField(ScoreFieldsForm)

    form = ScoreForm()

    players_list = []
    if current_user.is_authenticated:
        players = current_user.players
        players_list = [player.name for player in players]

    if request.form.get("add_player"):
        form.players.append_entry()
        for score in form.scores:
            score.append_entry()
    elif request.form.get("delete_player"):
        form.players.pop_entry()
        for score in form.scores:
            score.pop_entry()
    elif form.validate_on_submit():
        results = [[field[i].data for field in form.scores] for i in range(len(form.players.data))]
        if current_user.is_authenticated:
            new_session = Session(game_id=game.id, user_id=current_user.id,
                                  session_date=date.today(), field_names=json.dumps(fields))
            db.session.add(new_session)
            db.session.commit()
            players_list = form.players.data
            user_players = [player.name for player in current_user.players]
            for n, player_name in enumerate(players_list):
                if player_name not in user_players:
                    player = Player(name=player_name, user_id=current_user.id)
                    db.session.add(player)
                    db.session.commit()
                else:
                    player = db.session.scalar(
                        db.select(Player).filter_by(user_id=current_user.id).filter_by(name=player_name)
                    )
                player_result = PlayerResult(player_id=player.id,
                                             session_id=new_session.id,
                                             field_results=json.dumps(results[n]),
                                             result=sum(results[n]))
                db.session.add(player_result)
            db.session.commit()
            flash("Your game session has been saved!", "success")
            return redirect(url_for("profile.session_results", session_id=new_session.id))
        else:
            return render_template("results.html",
                                   form=form,
                                   results=results,
                                   fields=fields,
                                   number_of_fields=number_of_fields,
                                   number_of_players=number_of_players)

    return render_template("scoring.html",
                           form=form,
                           fields=fields,
                           number_of_fields=number_of_fields,
                           players_list=players_list,
                           game=game)
