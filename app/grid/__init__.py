from flask import Blueprint

grid = Blueprint('grid', __name__)

from . import views