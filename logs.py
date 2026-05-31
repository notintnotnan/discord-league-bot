import sys
import logging

from logging.handlers import RotatingFileHandler

logger = logging.getLogger("bot_logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelame)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = RotatingFileHandler("/logs/bot.log", maxBytes=50000, backupCount=3)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)