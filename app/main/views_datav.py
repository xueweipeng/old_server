# -*- coding:utf-8 -*-

from ..decorators import login_required
from . import main
from ..responses import JsonResult

from ..models import DataV
import time

import hashlib
import hmac
import base64

@main.route('/datav/<int:id>')
@login_required
def get_datav_url(id):
    return None

