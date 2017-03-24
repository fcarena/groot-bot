import yaml
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

from .getters import getpath
from .session import restart_session, with_session

CONFIG = 'config.yaml'


def add_debugger(handler):
    def decorated_handler(bot, update):
        print('---------------------------')
        print('<{}> invoked ...'.format(handler.__name__))
        print('user: ', update.message.from_user.first_name,
              'text: ', update.message.text)

        try:
            response = handler(bot, update)
        except err:
            print('An error occurred')
            print(err)

        print()
        return response

    return decorated_handler


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
        print('Awaking Groot...')

        self.updater.start_polling()
        self.updater.idle()

    @with_session
    def listen(self, telegram, conversation):
        responses, intents, entities = conversation.send_text(telegram.input_text)
        print('response.text:', responses)
        # TODO: lookup considering a context variable 'action'
        # TODO: call action
        # TODO: process response
        telegram.send_text(responses)

    @restart_session
    @with_session
    def start(self, telegram, conversation):
        responses, intents, entities = conversation.send_text('')
        print('response.text:', responses)
        telegram.send_text(responses)

    @with_session
    def help(self, telegram, _):
        telegram.send_text(
            'Meus criadores não me ensinaram a responder isso...')

def run():
    with open(CONFIG) as handler:
        groot = GrootBot(yaml.load(handler.read()))

    groot()
