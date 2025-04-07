import docker

import os
import time

from dotenv import load_dotenv

load_dotenv()


def is_container_ready(container):
    container.reload()
    return container.status == "running"


def wait_for_stable_status(container, stable_duration=3, interval=1):
    start_time = time.time()
    stable_count = 0
    while time.time() - start_time < stable_duration:
        if is_container_ready(container):
            stable_count += 1
        else:
            stable_count = 0

        if stable_count >= stable_duration / interval:
            return True

        time.sleep(interval)
    return False


def start_database_container():
    client = docker.from_env()
    container_name = "test-db"

    try:
        existing_container = client.containers.get(container_name)
        print(f"Container '{container_name}' exists. Stopping and removing...")
        existing_container.stop()
        existing_container.remove()
        print(f"Container '{container_name}' removed.")
    except docker.errors.NotFound:
        print(f"Container '{container_name}' does not exists.")

    configuration_config = {
        "name": container_name,
        "image": "postgres:16.1-alpine3.19",
        "detach": True,
        "ports": {"5432": "5434"},
        "environment": {
            "POSTGRES_USER": os.getenv("POSTGRES_USER"),
            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        },
    }

    container = client.containers.run(**configuration_config)

    while not is_container_ready(container):
        time.sleep(5)

    if not wait_for_stable_status(container):
        raise RuntimeError("Container did not stabilize within the specifed time.")
