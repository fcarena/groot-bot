from watson_developer_cloud import DiscoveryV1


class QueryService(object):
    def __init__(self, config):
        params = config['discovery']

        self.discovery = DiscoveryV1(
            username=params['discovery']['username'],
            password=params['discovery']['password'],
            version=params['discovery']['version']
        )

        self.environment_id = params['discovery']['environment_id']
        self.collection_id = params['discovery']['collection_id']

    def __call__(self, text):
        qopts = {'query': text}
        my_query = self.discovery.query(self.environment_id, self.collection_id, qopts)
        return my_query['results'][0]['html']
