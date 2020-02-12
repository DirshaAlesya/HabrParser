from telegram.ext import Updater, CommandHandler
import logging
import requests
from datetime import datetime
import time
from async_task import RepeatEvery
from gateway import DB
from Parser import HabrParser
import os


logger = logging.getLogger('HabrParser')
help_text = ''' Это бот который будет присылать статьи с Хабра'''

class HabrParserBot:
    def __init__(self, _token):
        self.sender = SendMsg(_token)
        self.gateway = DB()
        self.chat_id = None  # type: int
        self.habr = HabrParser()
        self.timer = RepeatEvery(1, self.check_link)
        self.timer.start()

        self.updater = Updater(token=_token)
        self.add_bot_handlers()
        self.updater.start_polling(poll_interval=2, timeout=30, read_latency=5)
        self.updater.idle()

    def add_bot_handlers(self):
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler('start', self.push_help_msg))
        dp.add_handler(CommandHandler('help', self.push_help_msg))
        dp.add_error_handler(self.error)

    @staticmethod
    def wait_sec(sec):
        while datetime.now().second != sec:
            time.sleep(1)

    def check_link(self):
        self.wait_sec(1)
        if not self.chat_id:
            return
        links = self.habr.parser()
        for link in links:
            result = self.gateway.insert(link)
            is_insert = int(result.split(" ")[2])
            if is_insert > 0:
                self.sender.push(link, self.chat_id)

    def push_help_msg(self, bot, update):
        self.chat_id = update.message.chat_id
        bot.send_message(chat_id=update.message.chat_id, text=help_text)

    @staticmethod
    def error(bot, update, err):
        logger.warning('Update "%s" caused error "%s"' % (update, err))


class SendMsg:
    def __init__(self, _token):
        self.token = _token

    def push(self, msg, chat_id):
        url = '{}{}{}'.format('https://api.telegram.org/bot', self.token, '/sendMessage')
        params = {'chat_id': chat_id, 'text': msg}
        try:
            requests.post(url, data=params)
        except Exception as er:
            logger.error('Send message error: {} - {}'.format(msg, er))


if __name__ == '__main__':
    HabrParserBot(os.environ['TOKEN'])