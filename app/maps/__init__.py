# -*- coding:utf-8 -*-

import os
from flask import Blueprint

maps = Blueprint('maps', __name__)

from . import views