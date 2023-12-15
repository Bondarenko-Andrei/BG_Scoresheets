from app import db, login_manager
from flask_login import UserMixin
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date


class Game(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    bgg_id: Mapped[Optional[int]]
    min_players: Mapped[Optional[int]]
    max_players: Mapped[Optional[int]]
    image: Mapped[Optional[str]]
    year: Mapped[Optional[int]]
    user_id = mapped_column(ForeignKey("user.id"), nullable=True)
    fields: Mapped[list["Field"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    author: Mapped["User"] = relationship(back_populates="custom_games")
    sessions: Mapped[list["Session"]] = relationship(back_populates="game", cascade="all, delete-orphan")


class Field(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id = mapped_column(ForeignKey("game.id"))
    name: Mapped[str]
    game: Mapped["Game"] = relationship(back_populates="fields")


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    bgg_username: Mapped[Optional[str]]
    password_hash: Mapped[Optional[str]]
    players: Mapped[list["Player"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    custom_games: Mapped[list["Game"]] = relationship(back_populates="author")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Player(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    user_id = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="players")
    sessions: Mapped[list["Session"]] = relationship(secondary="player_result", viewonly=True)
    results: Mapped[list["PlayerResult"]] = relationship(viewonly=True)


class Session(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id = mapped_column(ForeignKey("game.id"))
    user_id = mapped_column(ForeignKey("user.id"))
    session_date: Mapped[Optional[date]]
    field_names: Mapped[Optional[str]]
    results: Mapped[list["PlayerResult"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    players: Mapped[list["Player"]] = relationship(secondary="player_result", viewonly=True)
    user: Mapped["User"] = relationship()
    game: Mapped["Game"] = relationship(back_populates="sessions")


class PlayerResult(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id = mapped_column(ForeignKey("player.id"))
    session_id = mapped_column(ForeignKey("session.id"))
    field_results: Mapped[Optional[str]]
    result: Mapped[int]
    session: Mapped["Session"] = relationship(back_populates="results")
    player: Mapped["Player"] = relationship(back_populates="results")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
