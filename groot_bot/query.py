import re
import logging
from watson_developer_cloud import DiscoveryV1


class QueryService(object):
    H3_REGEX = re.compile('<h3>(.*)<\/h3>', re.UNICODE | re.MULTILINE | re.DOTALL)
    BODY_REGEX = re.compile('<body>(.*)<\/body>', re.UNICODE | re.MULTILINE | re.DOTALL)

    def __init__(self, config):
        params = config['discovery']

        self.discovery = DiscoveryV1(
            username=params['username'],
            password=params['password'],
            version=params['version']
        )

        self.environment_id = params['environment_id']
        self.collection_id_git = params['collection_id_git']
        self.collection_id_imp = params['collection_id_imp']

    def __call__(self, text, database):
        qopts = {'query': text}
        if database == 'git':
            my_query = self.discovery.query(self.environment_id, self.collection_id_git, qopts)
            result = my_query['results'][0]['html']
            match = self.H3_REGEX.findall(result)
        elif database == 'imp':
            my_query = self.discovery.query(self.environment_id, self.collection_id_imp, qopts)
            result = my_query['results'][0]['html']
            match = self.BODY_REGEX.findall(result)

        logging.debug('result %s match %s', result, match)
        return match[0]
