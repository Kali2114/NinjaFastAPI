import random
from app.models.ninja import Ninja
from app.models.village import Village
from app.models import enums


def create_ninja(session, **params):
    defaults = {
        "name": f"Ninja{random.randint(1, 9999)}",
        "clan": "Test",
        "rank": enums.RankEnum.genin,
        "jinchuriki": enums.JinchurikiEnum.none,
    }
    defaults.update(params)
    ninja = Ninja(**defaults)
    session.add(ninja)
    session.commit()
    session.refresh(ninja)
    return ninja


def create_village(session, **params):
    defaults = {
        "name": enums.VillageEnum.konoha,
        "country": enums.CountryEnum.fire,
        "kage_id": None,
    }
    defaults.update(params)
    village = Village(**defaults)
    session.add(village)
    session.commit()
    session.refresh(village)
    return village
