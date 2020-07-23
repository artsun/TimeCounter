# -*- coding: utf-8 -*-

from datetime import timedelta


def delta_to_hms(delta: timedelta) -> str:
    return f'{delta.seconds//3600} ч. {(delta.seconds//60)%60} мин. {delta.seconds%60} сек.'
