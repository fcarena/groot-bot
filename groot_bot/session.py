from functools import wraps
from datetime import datetime
from watson_developer_cloud import ConversationV1

from .getters import getpath, getpaths, getkeys

class TelegramSession(object):
    def __init__(self, bot, update, chat, user):
        self.bot = bot
        self.update = update
        self.chat, self.user = chat, user
        self.input_text = update.message.text

    def send(self, messages):
        print('telegram.send responses:', messages)
        return [
            self.bot.send_message(chat_id=self.chat['id'], **message)
            for message in messages
        ]

    def send_text(self, messages):
        if isinstance(messages, str):
            messages = [messages]

        print('telegram.send_text messages:', messages)
        return self.send([{'text': text} for text in messages])


class ConversationSession(object):
    def __init__(self, user, config):
        keys = getkeys(config['watson'], ['username', 'password', 'version'])
        print('keys:', keys)
        self.conversation = ConversationV1(**keys)
        print('conversation:', self.conversation)
        print('workspaces:', self.conversation.list_workspaces())

        self.workspace = getpath(config, 'watson.workspace')
        self.context = {}
        self.entities = []
        self.user = user
        self.started_at = datetime.now()

    def send(self, **kwargs):
        print('try conversation', kwargs, self.workspace)

        response = self.conversation.message(
            workspace_id=self.workspace,
            context=self.context,
            message_input=kwargs)
        print('Response:', response)

        self.entities = self.entities + response['entities']
        print('entities:', self.entities)
        self.context = response['context']
        print('context:', self.context)

        return getpaths(response, ['output.text', 'intents', 'entities'])

    def send_text(self, text):
        return self.send(text=text)

def restart_session(method):
    @wraps(method)
    def _method(self, bot, update):
        print('restarting session ...')
        print(type(bot), type(update), getattr(update, 'extract_chat_and_user', 'non-excsite'))
        _, user = update.extract_chat_and_user()

        self.brain.pop(user['id'], None)
        print('bot brain removed ...')
        return method(self, bot, update)

    return _method

def with_session(method):
    @wraps(method)
    def _method(self, bot, update):
        print('with session')
        chat, user = update.extract_chat_and_user()
        print('Telegram chat <', chat['id'], '>', 'for user <', user['id'], '>')

        session = self.brain.get(user['id'], None)
        telegram = TelegramSession(bot, update, chat, user)

        if session is None:
            conversation = ConversationSession(user, self.config)
            self.brain[user['id']] = conversation
        else:
            conversation = session

        print('Conversation:', conversation)
        print('Telegram:', telegram)

        return method(self, telegram, conversation)

    return _method
