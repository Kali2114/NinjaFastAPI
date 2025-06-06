from fastapi import FastAPI
import logging
import logging.config


logging.config.fileConfig("../logging.conf", disable_existing_loggers=False)

app = FastAPI()
