from app.models.enums import RankEnum


def ensure_alive(ninja):
    if not ninja.alive:
        raise RuntimeError("Ninja is dead")


def validate_ninja_can_join_team(ninja):
    if ninja.team:
        raise ValueError("Ninja is already a member of a team.")
    if ninja.rank == RankEnum.academy:
        raise ValueError("Academy students cannot join a team.")
