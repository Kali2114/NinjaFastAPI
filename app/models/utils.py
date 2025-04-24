def ensure_alive(ninja):
    if not ninja.alive:
        raise RuntimeError("Ninja is dead")
