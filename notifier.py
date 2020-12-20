# import telegram
import telepot


class TelegramNotifier:
    """Telegram Notifier"""

    def __init__(self, config):
        self.config = config
        self.chat_id = self.config.telegram_chat_id
        self.token = self.config.telegram_token
        # self.bot = telegram.Bot(token=self.token)
        self.bot = telepot.Bot(token=self.token)

    def send_message(self, msg_text, image_file=None):
        if image_file is not None:
            self.bot.sendPhoto(chat_id=self.chat_id, photo=open(image_file, 'rb'), caption=msg_text)
        else:
            self.bot.sendMessage(chat_id=self.chat_id, text=msg_text)
