import logging
from tradingbot.config import get_config

config = get_config()

# 1. DEBUG logger.debug("debug message")
# 2. INFO logger.info("info message")
# 3. WARNING logger.warning("warning message")
# 4. ERROR logger.error("error message")
# 5. CRITICAL logger.critical("critical message")


class LoggerFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("Trading bot")
logger.setLevel(logging.INFO)

if config["logfile"] == True:
    filehandler = logging.FileHandler("tradingbot.log")
    fileformatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
    )
    filehandler.setFormatter(fileformatter)
    logger.addHandler(filehandler)


streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)
streamhandler.setFormatter(LoggerFormatter())
logger.addHandler(streamhandler)
