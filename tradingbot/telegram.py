from abc import abstractmethod
from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, Updater


class Telegram:
    def __init__(self, config) -> None:
        self._config = config
        self._updater = Updater(config["telegram"]["token"])
        self._dispatcher = self._updater.dispatcher

        self._init_keyboard()
        self._add_handler()

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

    def send_message(self, msg: str) -> None:
        if self._config["telegram"]["enabled"] == True:
            self._updater.bot.send_message(
                chat_id=self._config["telegram"]["chat_id"],
                text=msg,
                disable_notification=True,
            )

    def _add_handler(self):
        handlers = [
            CommandHandler("help", self._help),
            CommandHandler("status", self._status),
            CommandHandler("profit", self._profit),
            CommandHandler("daily", self._daily),
            CommandHandler("balance", self._balance),
            CommandHandler("forcesell", self._forcesell),
        ]
        for handler in handlers:
            self._dispatcher.add_handler(handler)

    def _help(self, update, context) -> None:
        self.send_message(
            "Available commands:\n/status to get all trades status\n/profit get total profit since the start\n/daily get daily profit\n/balance get current balance in USDT\n/forcesell [ID] sell an open order\n"
        )

    def _status(self, update, context) -> None:
        self.send_message("/status not implemented yet")

    def _profit(self, update, context) -> None:
        self.send_message("/profit not implemented yet")

    def _daily(self, update, context) -> None:
        self.send_message("/daily not implemented yet")

    def _balance(self, update, context) -> None:
        self.send_message("/balance not implemented yet")

    def _forcesell(self, update, context) -> None:
        self.send_message("/forcesell not implemented yet")

    def clean(self) -> None:
        self._updater.stop()