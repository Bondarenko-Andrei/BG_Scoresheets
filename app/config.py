'''This is an example config for deployment on local machine. 
In production relevant values for SECRET_KEY and SQLALCHEMY_DATABASE_URI are (and should be) used'''

class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///games.db"
    FLASK_ADMIN_SWATCH = "cerulean"
