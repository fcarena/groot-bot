import yaml
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

CONFIG = 'config.yaml'

def debug(update, handler):
    print('---------------------------\n<{}> message received ...'.format(handler))
    print('user: ', update.message.from_user.first_name)
    print('text: ', update.message.text)
    print('\n\n\n')

def start(bot, update):
    debug(update, 'start')
    update.message.reply_text('Hello World!')

def chat(bot, update):
    debug(update, 'chat')
    bot.sendMessage(
        chat_id=update.message.chat_id,
        text='Hello {}'.format(update.message.from_user.first_name))

def run():
    print('Starting Bot ...')

    with open(CONFIG) as handler:
        config = yaml.load(handler.read())

    updater = Updater(token=config['token'])

    commands = [start]
    handlers = [CommandHandler(cmd.__name__, cmd) for cmd in commands]
    [updater.dispatcher.add_handler(handler) for handler in handlers]

    updater.dispatcher.add_handler(MessageHandler(Filters.all, chat))

    updater.start_polling()
    updater.idle()

