# -*- coding: utf-8 -*-

from flask_login import current_user
from datetime import timedelta


def define_current_user(current_user: current_user) -> str:
    is_anon = (current_user.is_active, current_user.is_authenticated, current_user.is_anonymous)
    return '' if is_anon == (False, False, True) else current_user.name


def delta_to_hms(delta: timedelta) -> str:
    return f'{delta.seconds//3600} ч. {(delta.seconds//60)%60} мин. {delta.seconds%60} сек.'
