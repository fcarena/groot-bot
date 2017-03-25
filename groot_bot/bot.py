import logging
import yaml
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

from .getters import getpath
from .session import restart_session, with_session

CONFIG = 'config.yaml'


def add_debugger(handler):
    def _handler(bot, update):
        logging.debug('<%s> invoked ...\nuser: %s, text: %s',
                      handler.__name__,
                      update.message.from_user.first_name,
                      update.message.text)

        try:
            response = handler(bot, update)
        except err:
            logging.exception(
                'An error occurred while calling handler: %s', err)

        return response

    return _handler


class GrootBot(object):
    commands = 'start help'.split(' ')

    def __init__(self, config):
        self.config = config
        self.updater = Updater(token=getpath(config, 'telegram.token'))

        self.handlers = [
            CommandHandler(command, add_debugger(getattr(self, command)))
            for command in self.commands
        ] + [MessageHandler(Filters.all, add_debugger(self.listen))]

        dispatcher = self.updater.dispatcher
        [dispatcher.add_handler(handler) for handler in self.handlers]

        # Robot state (considering conversation API)
        self.brain = {}

    def __call__(self):
        logging.info('Awaking Groot...')

        self.updater.start_polling()
        self.updater.idle()

    @with_session
    def listen(self, telegram, conversation):
        responses, intents, entities = conversation.send_text(telegram.input_text)
        logging.debug('responses: %s', responses)
        # TODO: lookup considering a context variable 'action'
        # TODO: call action
        # TODO: process response
        telegram.send_text(responses)

    @restart_session
    @with_session
    def start(self, telegram, conversation):
        responses, intents, entities = conversation.send_text('')
        logging.debug('responses: %s', responses)
        telegram.send_text(responses)

    @with_session
    def help(self, telegram, _):
        telegram.send_text(
            'Meus criadores não me ensinaram a responder isso...')

def run():
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s')

    with open(CONFIG) as handler:
        groot = GrootBot(yaml.load(handler.read()))

    groot()
