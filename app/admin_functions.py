from app import app, db
from app.models import Game
from app.custom.bgg_requests import _get_game_dict
import requests
import xml.etree.ElementTree as ET


def update_db_from_bgg():
    with app.app_context():
        res = db.session.scalars(db.select(Game.bgg_id)).all()
        ids = ",".join([str(bgg_id) for bgg_id in res if bgg_id])
        params = {"id": ids, "thing": "boardgame"}
        bgg_url = "https://boardgamegeek.com/xmlapi2/thing"
        game_xml = requests.get(bgg_url, params=params).text
        root = ET.fromstring(game_xml)
        for elem in root:
            bgg_game = _get_game_dict(elem, extended=True)
            games = db.session.scalars(db.select(Game).filter_by(bgg_id=bgg_game["id"]))
            for game in games:
                game.image = bgg_game["image"]
                game.name = bgg_game["name"]
                game.year = bgg_game["year"]
                game.min_players = bgg_game["min_players"]
                game.max_players = bgg_game["max_players"]
            db.session.commit()
