from tradingbot.bot import Bot


def main() -> None:
    try:
        bot = Bot()
        bot.run()
    except ValueError:
        print("ERROR: Oops! An error occured")
    except KeyboardInterrupt:
        print("ERROR: SIGINT received, aborting ...")
    finally:
        if bot:
            bot.clean()


if __name__ == "__main__":
    main()
