from genshin import fetch_genshin
from starrail import fetch_starrail
from ww import fetch_ww

def fetch_all():

    results = []

    results.extend(fetch_genshin())
    results.extend(fetch_starrail())
    results.extend(fetch_ww())

    return results