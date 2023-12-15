import requests
import xml.etree.ElementTree as ET
from time import sleep


def _get_game_dict(elem, extended=False):
    game = {"id": elem.attrib.get("id"), "name": elem.find("name").attrib["value"]}
    for name in elem.findall("name"):
        if name.attrib["type"] == "primary":
            game["name"] = name.attrib["value"]
            break
    image = elem.find("image")
    game["image"] = image.text if image is not None else None
    year = elem.find("yearpublished")
    game["year"] = year.attrib["value"] if year is not None else None
    if extended:
        min_players = elem.find("minplayers")
        max_players = elem.find("maxplayers")
        game["min_players"] = int(min_players.attrib["value"]) if min_players is not None else None
        game["max_players"] = int(max_players.attrib["value"]) if max_players is not None else None
    return game


def get_collection_data(params):
    bgg_url = "https://boardgamegeek.com/xmlapi2/collection"
    bgg_request = requests.get(bgg_url, params)
    while bgg_request.status_code != 200:
        sleep(0.5)
        bgg_request = requests.get(bgg_url, params)
    xml = bgg_request.text
    root = ET.fromstring(xml)
    group = []
    for elem in root:
        game = {"id": elem.attrib.get("objectid"), "name": elem.find("name").text}
        image = elem.find("image")
        game["image"] = image.text if image is not None else None
        year = elem.find("yearpublished")
        game["year"] = year.text if year is not None else None
        group.append(game)
    return group


def get_game_data(bgg_id):
    params = {"id": bgg_id, "thing": "boardgame"}
    bgg_url = "https://boardgamegeek.com/xmlapi2/thing"
    game_xml = requests.get(bgg_url, params=params).text
    root = ET.fromstring(game_xml)
    if len(root) == 0:
        return False
    elem = root[0]
    game = _get_game_dict(elem, extended=True)
    return game


def get_search_data(game: str):
    bgg_search_url = "https://boardgamegeek.com/xmlapi2/search"
    search_params = {"query": game.replace(" ", "+"), "type": "boardgame,boardgameexpansion"}
    search_xml = requests.get(bgg_search_url, params=search_params).text
    root = ET.fromstring(search_xml)
    game_ids = []
    exp_ids = []
    for elem in root:
        elem_id = elem.attrib.get("id")
        elem_type = elem.attrib.get("type")
        if elem_type == "boardgame":
            game_ids.append(elem_id)
        elif elem_type == "boardgameexpansion":
            if elem_id in game_ids:
                game_ids.remove(elem_id)
            exp_ids.append(elem_id)
    ids = ",".join([*game_ids, *exp_ids])
    boardgames = []
    expansions = []
    bgg_games_url = "https://boardgamegeek.com/xmlapi2/thing"
    game_xml = requests.get(bgg_games_url, params={"id": ids}).text
    root = ET.fromstring(game_xml)
    for elem in root:
        game = _get_game_dict(elem)
        if game["id"] in game_ids:
            boardgames.append(game)
        elif game["id"] in exp_ids:
            expansions.append(game)
    return boardgames, expansions
