# -*- coding: utf-8 -*-

from flask_login import current_user


def define_current_user(current_user: current_user) -> str:
    is_anon = (current_user.is_active, current_user.is_authenticated, current_user.is_anonymous)
    return '' if is_anon == (False, False, True) else current_user.name
