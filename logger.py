# logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_PATH = "events.log"
os.makedirs(os.path.dirname(LOG_PATH) or ".", exist_ok=True)

logger = logging.getLogger("gestor_pedidos")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

# helper
def info(msg: str):
    logger.info(msg)

def error(msg: str):
    logger.error(msg)
