from tradingbot.bot import Bot


def main() -> None:
    try:
        bot = Bot()
        bot.run()
    except ValueError:
        print("Oops! An error occured")
    except KeyboardInterrupt:
        print("SIGINT received, aborting ...")
    finally:
        if bot:
            bot.clean()


if __name__ == "__main__":
    main()
