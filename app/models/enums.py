import enum


class RankEnum(enum.Enum):
    academy = "academy"
    genin = "genin"
    chunin = "chunin"
    jonin = "jonin"
    anbu = "anbu"
    kage = "kage"


class KekkeiGenkaiEnum(enum.Enum):
    sharingan = "sharingan"
    byakugan = "byakugan"
    rinnegan = "rinnegan"
    wood_release = "wood_release"
    none = "none"


class JinchurikiEnum(enum.Enum):
    shukaku = "Shukaku"
    matatabi = "Matatabi"
    isobu = "Isobu"
    son_goku = "Son Goku"
    kokuo = "Kokuo"
    saiken = "Saiken"
    choumei = "Choumei"
    gyuki = "Gyuki"
    kurama = "Kurama"
    juubi = "Juubi"
    none = "None"


LEVEL_THRESHOLDS = {
    1: 0,
    2: 100,
    3: 250,
    4: 450,
    5: 700,
    6: 1000,
    7: 1350,
    8: 1750,
    9: 2200,
    10: 2700,
}


CHAKRA_THRESHOLDS = {
    1: 100,
    2: 120,
    3: 150,
    4: 190,
    5: 240,
    6: 300,
    7: 370,
    8: 450,
    9: 540,
    10: 640,
}
