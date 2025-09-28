from faker import Faker

from app.models import User
from app.auth.hashing import hash_password


faker = Faker()


class Ninja:
    def __init__(self, id, name, clan, user_id):
        self.id = id
        self.name = name
        self.clan = clan
        self.user_id = user_id


def get_random_ninja_dict():
    return {
        "id": faker.random_int(1, 100),
        "name": faker.name(),
        "clan": faker.name(),
        "user_id": faker.random_int(1, 100),
    }


def create_test_user(db_session, username=None, password="test_pass", email=None):
    username = username or faker.name()
    email = email or faker.email()
    user = User(username=username, hashed_password=hash_password(password), email=email)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
