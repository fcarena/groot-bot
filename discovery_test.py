import sys
import os
import json
from watson_developer_cloud import DiscoveryV1

discovery = DiscoveryV1(
  username="a29e2e26-b7f7-46d2-9238-2844de9e398c",
  password="mMqj2iZesUVL",
  version="2016-12-01"
)

qopts = {'query': "como criar um repositorio"}
my_query = discovery.query('2fe9a94b-4655-4547-a179-896176b4bbf8', 'b2578d25-876c-412a-ae5f-1e562648f446', qopts)
print(json.dumps(my_query, indent=2))



