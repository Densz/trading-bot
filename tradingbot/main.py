from tradingbot.logger import logger
from tradingbot.bot import Bot


def main() -> None:
    try:
        bot = Bot()
        bot.run()
    except ValueError:
        logger.error("Oops! An error occured")
    except KeyboardInterrupt:
        logger.error("SIGINT received, aborting ...")
    finally:
        if bot:
            bot.clean()


if __name__ == "__main__":
    main()
