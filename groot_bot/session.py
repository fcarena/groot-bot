import logging

from functools import wraps
from datetime import datetime

from emoji import emojize
from watson_developer_cloud import ConversationV1

from .getters import getpath, getpaths, getkeys

logging.basicConfig(
    level=logging.DEBUG,
        format='%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s')

class TelegramSession(object):
    def __init__(self, bot, update, chat, user):
        self.bot = bot
        self.update = update
        self.chat, self.user = chat, user
        self.input_text = update.message.text

    def send(self, messages):
        logging.debug('messages: %s', messages)
        return [
            self.bot.send_message(chat_id=self.chat['id'], **message)
            for message in messages
        ]

    def send_text(self, messages):
        if isinstance(messages, str):
            messages = [messages]

        logging.debug('messages: %s', messages)
        return self.send([
            {'text': emojize(text, use_aliases=True)}
            for text in messages
        ])


class ConversationSession(object):
    def __init__(self, user, config):
        keys = getkeys(config['watson'], ['username', 'password', 'version'])
        logging.debug('keys:', keys)
        self.conversation = ConversationV1(**keys)
        logging.debug('conversation: %s', self.conversation)
        logging.debug('workspaces: %s', self.conversation.list_workspaces())

        self.workspace = getpath(config, 'watson.workspace')
        self.context = {}
        self.entities = []
        self.user = user
        self.started_at = datetime.now()

    def send(self, **kwargs):
        logging.debug('kwargs: %s, workspace: %s', kwargs, self.workspace)

        response = self.conversation.message(
            workspace_id=self.workspace,
            context=self.context,
            message_input=kwargs)
        logging.debug('response: %s', response)

        self.entities = self.entities + response['entities']
        logging.debug('entities: %s', self.entities)
        self.context = response['context']
        logging.debug('context: %s', self.context)

        return getpaths(response, ['output.text', 'intents', 'entities'])

    def send_text(self, text):
        return self.send(text=text)

def restart_session(method):
    @wraps(method)
    def _method(self, bot, update):
        logging.info('Restarting session ...')
        logging.debug('bot: %s, update: %s, method: %s',
            type(bot), type(update),
            getattr(update, 'extract_chat_and_user', 'not-defined'))
        _, user = update.extract_chat_and_user()

        self.brain.pop(user['id'], None)
        logging.info('Bot brain removed!')
        return method(self, bot, update)

    return _method

def with_session(method):
    @wraps(method)
    def _method(self, bot, update):
        logging.debug('with_session')
        chat, user = update.extract_chat_and_user()
        logging.debug('Telegram chat <%s> for user <%s>',
                      chat['id'], user['id'])

        session = self.brain.get(user['id'], None)
        telegram = TelegramSession(bot, update, chat, user)

        if session is None:
            conversation = ConversationSession(user, self.config)
            self.brain[user['id']] = conversation
        else:
            conversation = session

        logging.debug('conversation: %s', conversation)
        logging.debug('telegram: %s', telegram)

        return method(self, telegram, conversation)

    return _method
