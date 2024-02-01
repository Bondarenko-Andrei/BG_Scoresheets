# BG-Scoresheets

A simple web application for scoring boardgame plays.

## 📖 General info

A bunch of boardgames, that involve somewhat complicated scoring, come with paper scoresheets aimed at simplifying the scoring process.
At the same time the game itself usually doesn't involve any "pen and paper" routine, so the scoring process becomes a separate activity.
And those scoresheets while sharing common layout are unique for each game due to unique scoring categories and varying number of possible players.

The idea behind this app was to develop a simple digital resource, which would provide some additional quality of life features alongside removing the necessity of using pen and paper.

While trying to keep it simple and focusing on replacing paper scoresheets with their digital analogue, the app also allows to save game session results and player info, creating custom scoresheets, as well as
provides integration with [BoardGameGeek](https://boardgamegeek.com/), the most popular and complete boardgame web resource out there.

## 📝 Features

This app currently has following features:

- Boardgame scoring interface
- Built-in scoresheets for several popular boardgames
- Custom scoresheet creating interface
- Saving game session results
- Saving player data and player data autocomplete on scoring
- Integration with [BoardGameGeek](https://boardgamegeek.com/) (BGG):
    * Game image uploading
    * Finding boardgames via BGG search engine
    * Choosing games from user's collection on BGG
- User accounts storing data accessible via profile page:
    * Custom scoresheets
    * Players
    * Game sessions

To use most of the app features (except for scoring with pre-made scoresheets) registration is required as most of the data stored is tied to unqiue user and is not supposed to be available for other users.

## 🌐 Website

The app is currently deployed at [PythonAnywhere.com](https://bgscoresheets.pythonanywhere.com)

## ⚙️ Technologies

- Python 3.12
- Flask
- Jinja2
- WTForms
- SQLAlchemy
- Bootstrap

## 
