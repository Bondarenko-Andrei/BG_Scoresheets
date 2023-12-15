from flask import render_template, url_for, redirect, request, flash, session
from flask_login import current_user, login_required
from app import db
from app.custom import bp_custom
from app.models import Game, Field
from app.custom.forms import SearchGameForm, CustomSetFieldsForm, BggIdForm, CustomCreate
from app.custom.bgg_requests import get_collection_data, get_search_data, get_game_data


@bp_custom.route("/choose_option", methods=("GET", "POST"))
@login_required
def choose_option():
    search_form = SearchGameForm()
    bgg_id_form = BggIdForm()

    if search_form.validate_on_submit():
        return redirect(url_for("custom.search_results", game=search_form.game_name.data))
    elif bgg_id_form.validate_on_submit():
        return redirect(url_for("custom.set_fields", bgg_id=bgg_id_form.bgg_id.data))
    return render_template("choose_option.html", search_form=search_form, bgg_id_form=bgg_id_form)


@bp_custom.route("/search_results/<game>")
@login_required
def search_results(game: str):
    boardgames, expansions = get_search_data(game)
    return render_template("search_results.html", boardgames=boardgames, expansions=expansions)


@bp_custom.route("/custom/<bgg_id>", methods=("GET", "POST"))
@login_required
def set_fields(bgg_id):
    if request.method == "GET":
        game = get_game_data(bgg_id)
        if not game:
            flash("No game with indicated ID found. Please try again!", "warning")
            return redirect(url_for("custom.choose_option"))
        session["game"] = game

    game = session["game"]

    form = CustomSetFieldsForm()

    if request.form.get("add_field"):
        form.fields.append_entry()
    elif request.form.get("delete_field"):
        if form.fields.data:
            form.fields.pop_entry()
    elif form.validate_on_submit():
        fields = [Field(name=field.data) for field in form.fields]
        new_game = Game(name=game["name"],
                        bgg_id=bgg_id,
                        min_players=game["min_players"],
                        max_players=game["max_players"],
                        image=game["image"],
                        fields=fields,
                        user_id=current_user.id)
        db.session.add(new_game)
        db.session.commit()
        flash(f"Your scoresheet for {new_game.name} has been created!", "success")
        del session["game"]
        return redirect(url_for("index"))

    return render_template("set_fields.html", form=form, game=game)


@bp_custom.route("/my_games")
@login_required
def my_games():
    bgg_username = current_user.bgg_username
    if not bgg_username:
        flash("BGG username required to select game from collection", "warning")
        return redirect(url_for("custom.choose_option"))
    game_params = {"username": bgg_username, "excludesubtype": "boardgameexpansion"}
    boardgames = get_collection_data(game_params)
    exp_params = {"username": bgg_username, "subtype": "boardgameexpansion"}
    expansions = get_collection_data(exp_params)
    return render_template("search_results.html", boardgames=boardgames, expansions=expansions)


@bp_custom.route("/custom_create", methods=("GET", "POST"))
@login_required
def custom_create():
    form = CustomCreate()

    if request.form.get("add_field"):
        form.fields.append_entry()
    elif request.form.get("delete_field"):
        if form.fields.data:
            form.fields.pop_entry()
    elif form.validate_on_submit():
        fields = [Field(name=field.data) for field in form.fields]
        new_game = Game(name=form.name.data,
                        min_players=form.min_players.data,
                        max_players=form.max_players.data,
                        fields=fields,
                        user_id=current_user.id)
        db.session.add(new_game)
        db.session.commit()
        flash(f"Your scoresheet for {new_game.name} has been created!", "success")
        return redirect(url_for("index"))

    return render_template("custom_create.html", form=form)
