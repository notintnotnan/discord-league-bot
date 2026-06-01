import sys
import logging

from logging.handlers import RotatingFileHandler

class RichFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[1;31m'  # Bold Red
    }
    RESET = '\033[0m'

    def format(self, record):
        original_lvlname = record.levelname
        color = self.COLORS.get(original_lvlname, self.RESET)

        record.levelname = f"{color}{original_lvlname}{self.RESET}"

        result = super().format(record)

        record.levelname = original_lvlname

        return result

log_format = '%(asctime)s [%(levelname)s] %(message)s'
timestamp_format = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("bot_logger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(RichFormatter(log_format, timestamp_format))

file_handler = RotatingFileHandler("./logs/bot.log", maxBytes=50000, backupCount=3)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(log_format, timestamp_format))

logger.addHandler(console_handler)
logger.addHandler(file_handler)