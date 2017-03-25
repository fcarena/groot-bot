import re
from watson_developer_cloud import DiscoveryV1


class QueryService(object):
    BODY_REGEX = re.compile('<h3>(.*)<\/h3>', re.U)

    def __init__(self, config):
        params = config['discovery']

        self.discovery = DiscoveryV1(
            username=params['username'],
            password=params['password'],
            version=params['version']
        )

        self.environment_id = params['environment_id']
        self.collection_id = params['collection_id']

    def __call__(self, text):
        qopts = {'query': text}
        my_query = self.discovery.query(self.environment_id, self.collection_id, qopts)
        result = my_query['results'][0]['html']
        match = self.BODY_REGEX.findall(result)
        return match[0]
