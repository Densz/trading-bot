from abc import abstractmethod
from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater


class Telegram:
    def __init__(self, config) -> None:
        self._config = config
        self._updater = Updater(config["telegram"]["token"])
        self._dispatcher = self._updater.dispatcher

        self._init_keyboard()
        self._updater.start_polling()

    def _init_keyboard(self) -> None:
        reply_markup = ReplyKeyboardMarkup(
            [
                ["/status", "/profit", "/daily"],
                ["/balance", "/forcesell", "/help"],
            ],
            resize_keyboard=True,
        )
        self._updater.bot.send_message(
            chat_id=self._config["telegram"]["chat_id"],
            text=f"{'📄 PAPER_MODE' if self._config['paper_mode'] else '💵 LIVE MODE'} -> Bot is Trading !",
            reply_markup=reply_markup,
            disable_notification=True,
        )

    @abstractmethod
    def send_message(self, msg: str) -> None:
        if self._config["telegram"]["enabled"] == True:
            self._updater.bot.send_message(
                chat_id=self._config["telegram"]["chat_id"],
                text=msg,
                disable_notification=True,
            )

    def clean(self) -> None:
        self._updater.stop()