# -*- coding:utf-8 -*-

import os
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
from . import views_datav
