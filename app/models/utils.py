import os

from app.models.enums import RankEnum
from uuid import uuid4


def ensure_alive(ninja):
    if not ninja.alive:
        raise RuntimeError("Ninja is dead")


def validate_ninja_can_join_team(ninja):
    if ninja.team:
        raise ValueError("Ninja is already a member of a team")
    if ninja.rank == RankEnum.academy:
        raise ValueError("Academy students cannot join a team")


def validate_set_kage(ninja, village):
    if ninja.rank != RankEnum.kage:
        raise ValueError("Only kage ninja rank can be a kage of village")
    if ninja.village != village:
        raise ValueError("Only member of village can be a kage")
    if village.kage:
        raise ValueError("Village already has a kage")


def generate_avatar_name(name):
    base_name, ext = os.path.splitext(name)
    new_name = str(uuid4()) + ext
    return new_name
