import logging

from datetime import datetime
from functools import wraps

from watson_developer_cloud import ConversationV1

from .getters import getpath, getpaths, getkeys


def with_conversation(method):
    @wraps(method)
    def _method(groot, user, text):
        logging.debug('Retrieving Watson conversation interface...')

        session = groot.brain.get(user['id'], {})
        conversation = (
            session.get('conversation', None) or
            ConversationSession(user, self.config)
        )

        logging.debug('conversation: %s', conversation)

        return method(groot, user, text, conversation)

    return _method


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

    def send(self, context=None, **kwargs):
        logging.debug('kwargs: %s, workspace: %s', kwargs, self.workspace)

        self.context = {**self.context, **(context or {})}
        logging.debug('context: %s', self.context)

        response = self.conversation.message(
            workspace_id=self.workspace,
            context=self.context,
            message_input=kwargs)
        logging.debug('response: %s', response)

        self.entities = self.entities + response['entities']
        logging.debug('entities: %s', self.entities)
        self.context = response['context']
        logging.debug('new context: %s', self.context)

        return response
