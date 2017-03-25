import logging
import yaml

from functools import wraps

from emoji import emojize
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

from .getters import getpath, getkeys
from .conversation import with_conversation
from .query import QueryService

CONFIG = 'config.yaml'


class GrootBot(object):
    commands = 'start help'.split(' ')

    def __init__(self, config):
        self.config = config
        self.updater = Updater(token=getpath(config, 'telegram.token'))

        self.handlers = [
            CommandHandler(command, self.create_handler(getattr(self, command)))
            for command in self.commands
        ] + [
            MessageHandler(Filters.all, self.create_handler(self.answer))
        ]

        dispatcher = self.updater.dispatcher
        [dispatcher.add_handler(handler) for handler in self.handlers]

        # Robot state
        self.brain = {}
        self.query = QueryService(self.config)

    def __call__(self):
        logging.info('Awaking Groot...')

        self.updater.start_polling()
        self.updater.idle()

    def create_handler(self, callback, type='message'):
        @wraps(callback)
        def _handler(bot, update):
            chat, user = update.extract_chat_and_user()
            logging.debug(
                'callback <%s>, user <%s>, chat <%s>',
                callback.__name__,
                getpath(user, 'username', user['id']),
                chat['id']
            )
            text = update.extract_message_text()

            return self.process_responses(bot, chat, callback(user, text))

        return _handler

    def process_responses(self, bot, chat, responses):
        if not isinstance(responses, list):
            responses = [responses]

        logging.debug('%d responses', len(responses))
        return [
            self.process_response(bot, chat, response)
            for response in responses
        ]

    def process_response(self, bot, chat, response):
        if isinstance(response, str):
            response = dict(text=response, parse_mode='HTML')

        text = response.get('text', None)
        if text is not None:
            response['text'] = emojize(text, use_aliases=True)

        logging.debug('response: %s', response)
        return bot.send_message(chat_id=chat['id'], **response)

    @with_conversation
    def answer(self, user, text, conversation):
        response = conversation.send(
            text=text,
            context=dict(
                user=getkeys(user, [
                    'username',
                    'last_name',
                    'first_name'
                ])
            )
        )
        logging.debug('responses: %s', response)

        texts = getpath(response, 'output.text')
        if(len(texts) > 1 and texts[0] == ''):
            texts = texts[1:]

        if texts is None:
            raise ValueError('Conversation response should not be empty')

        entities = response['entities']

        target = None
        for entity in entities:
            if entity['entity'] == 'target':
                target = entity['value']

        if target:
            logging.info('Accessing discovery ...')
            doubt = getpath(response, 'input.text')
            texts.insert(1, self.query(doubt, target))

        return texts

    def start(self, user, _):
        logging.info('Restarting bot brain ...')
        self.brain[user['id']] = {}

        return self.answer(user, '')

    def help(self, user, _):
        return dict(text='Meus criadores não me ensinaram a responder isso...')

def run():
    logging.basicConfig(
            level=logging.DEBUG,
            format='%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s')

    with open(CONFIG) as handler:
        groot = GrootBot(yaml.load(handler.read()))

    groot()
