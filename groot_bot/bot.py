import logging
import yaml

from functools import wraps

from emoji import emojize
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

from .getters import getpath
from .conversation import with_conversation
from .query import QueryService

CONFIG = 'config.yaml'


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

        # Robot state
        self.brain = {}
        query = QueryService(self.config)

    def __call__(self):
        logging.info('Awaking Groot...')

        self.updater.start_polling()
        self.updater.idle()

    def create_handler(self, callback, type='message'):
        @wraps(callback)
        def _handler(obj, bot, update):
            chat, user = update.extract_chat_and_user()
            logging.debug(
                'callback <%s>, user <%s>, chat <%s>',
                callback.__name__, user.get('username', user['id']), chat['id']
            )
            text = update.extract_message_text()

            return self.proccess_responses(bot, chat, callback(obj, user, text))

        return _handler

    def process_responses(self, bot, chat, responses):
        if isinstance(response, dict):
            responses = [responses]

        logging.debug('%d responses', len(responses))
        return [self.process_response(response) for response in responses]

    def process_response(self, bot, chat, response):
        if isinstance(response, str):
            response = dict(text=text, parse_mode='HTML')

        text = response.get('text', None)
        if text is not None:
            response['text'] = emojize(text, use_aliases=True)

        logging.debug('response: %s', response)
        return bot.send_message(chat_id=chat['id'], **response)

    @with_conversation
    def answer(self, user, text, conversation):
        responses = conversation.send(text=text, context=dict(user=user))
        logging.debug('responses: %s', responses)

        text = getpath(responses, 'output.text')
        if text is None:
            raise ValueError('Conversation response should not be empty')

        action = responses['context'].get('action', None)
        if action == 'query':
            text = self.query(text)

        return text

    def start(self, user, _):
        logging.info('Restarting bot brain ...')
        self.brain[user['id']] = {}

        return self.listen(user, '')

    def help(self, user, _):
        return dict(text='Meus criadores não me ensinaram a responder isso...')

def run():
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s')

    with open(CONFIG) as handler:
        groot = GrootBot(yaml.load(handler.read()))

    groot()
