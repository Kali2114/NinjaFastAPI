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


class CountryEnum(enum.Enum):
    fire = "Fire Country"
    water = "Water Country"
    wind = "Wind Country"
    earth = "Earth Country"
    lightning = "Lightning Country"
    rain = "Rain Country"
    grass = "Grass Country"
    sound = "Sound Country"
    waterfall = "Waterfall Country"
    iron = "Iron Country"
    moon = "Moon Country"
    sky = "Sky Country"
    sea = "Sea Country"
    swamp = "Swamp Country"
    hot_springs = "Hot Springs Country"
    frost = "Frost Country"
    claw = "Claw Country"
    fang = "Fang Country"
    wave = "Wave Country"


class VillageEnum(enum.Enum):
    konoha = "Hidden Leaf Village"
    suna = "Hidden Sand Village"
    kiri = "Hidden Mist Village"
    kumo = "Hidden Cloud Village"
    iwa = "Hidden Stone Village"
    oto = "Hidden Sound Village"
    ame = "Hidden Rain Village"
    kusa = "Hidden Grass Village"
    taki = "Hidden Waterfall Village"
    yuki = "Hidden Snow Village"
    uzushiogakure = "Hidden Whirlpool Village"
    hoshigakure = "Hidden Star Village"
    yugakure = "Hidden Hot Water Village"


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
