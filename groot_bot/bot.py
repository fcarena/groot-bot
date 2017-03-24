import yaml
from datetime import datetime
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from watson_developer_cloud import ConversationV1

from .getters import getpath, getpaths, getkeys

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


class ConversationSession(object):
    def __init__(self, user, config):
        keys = getkeys(config['watson'], ['username', 'password', 'version'])
        print('keys:', keys)
        self.conversation = ConversationV1(**keys)
        print('conversation:', conversation)
        print('workspaces:', conversation.list_workspaces())

        self.workspace_id = getpath(config, 'watson.workspace')
        self.context = {}
        self.entities = []
        self.user = user
        self.started_at = datetime.now()

    def x(self):
        print('inside x')

    def message(self, **kwargs):
        print('try conversation', kwargs, self.workspace)

        response = self.conversation.message(
            workspace_id=self.workspace, context=self.context, **kwargs)
        print('Response:', response)

        self.entities += response['entities']
        self.context = response['context']

        return getpaths(response, ['output.text', 'intents', 'entities'])


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

    def recover_session(self, update):
        user = self.recover_user(update)
        session = self.brain.get(user['id'], None)

        if session is None:
            session = ConversationSession(user, self.config)
            self.brain[user['id']] = session

        return session

    def recover_user(self, update):
        return getpath(update, 'message.from_user')

    def help(self, bot, update):
        chat, name = getpaths(
            update, ['message.chat_id', 'message.from_user.first_name'])

        bot.send_message(chat_id=chat, text='Hi {}, I am Groot!'.format(name))

    def listen(self, bot, update):
        chat, text = getpaths(update, ['message.chat_id', 'message.text'])

        session = self.recover_session(update)
        print('Session:', session)
        session.x()
        session.message(text=text)

        bot.send_message(chat_id=chat, text='Hi {}, I am Groot!'.format(name))

    def start(bot, update):
        update.message.reply_text("I'm Groot!")

def run():
    with open(CONFIG) as handler:
        groot = GrootBot(yaml.load(handler.read()))

    groot()
