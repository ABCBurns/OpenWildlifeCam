import telegram


class TelegramNotifier:
    """Telegram Notifier"""

    def __init__(self, config):
        self.config = config
        self.chat_id = self.config.telegram_chat_id
        self.token = self.config.telegram_token
        self.bot = telegram.Bot(token=self.token)

    def send_message(self, msg_text):
        self.bot.sendMessage(chat_id=self.chat_id, text=msg_text)
