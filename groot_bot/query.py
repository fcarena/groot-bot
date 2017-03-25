import re
from watson_developer_cloud import DiscoveryV1


class QueryService(object):
    BODY_REGEX = re.compile('<h3>(.*)<\/h3>', re.U)
    HTML_REGEX = re.compile('<html>(.*)<\/html>', re.U)

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
        if database == 'Git':
            my_query = self.discovery.query(self.environment_id, self.collection_id_git, qopts)
            result = my_query['results'][0]['html']
            match = self.BODY_REGEX.findall(result)
        elif database == 'Impressora':
            my_query = self.discovery.query(self.environment_id, self.collection_id_imp, qopts)
            result = my_query['results'][0]['html']
            match = self.HTML_REGEX.findall(result)
        return match[0]
