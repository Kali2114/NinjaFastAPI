import docker
import psycopg2

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


def wait_for_postgres(container, host="127.0.0.1", port=5434, timeout=20):
    print("Waiting for PostgreSQL to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            conn = psycopg2.connect(
                dbname="ninjadb",
                user="kamileg",
                password="553355",
                host=host,
                port=port,
            )
            conn.close()
            print("✅ PostgreSQL is ready!")
            return
        except psycopg2.OperationalError:
            time.sleep(1)
    raise TimeoutError("❌ PostgreSQL did not start in time.")


def start_database_container():
    client = docker.from_env()
    scripts_dir = os.path.abspath("./scripts")
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
            "POSTGRES_USER": "kamileg",
            "POSTGRES_PASSWORD": "553355",
            "POSTGRES_DB": "ninjadb",
        },
        "volumes": [f"{scripts_dir}:/docker-entrypoint-initdb.d"],
        "network": "ninjafastapi-development_default",
    }

    container = client.containers.run(**configuration_config)
    wait_for_postgres(container)

    while not is_container_ready(container):
        time.sleep(1)

    if not wait_for_stable_status(container):
        raise RuntimeError("Container did not stabilize within the specified time.")

    return container
