import requests
from requests.auth import HTTPBasicAuth
import os
import json
from watson_developer_cloud import DiscoveryV1

discovery = DiscoveryV1(
  username="a29e2e26-b7f7-46d2-9238-2844de9e398c",
  password="mMqj2iZesUVL",
  version="2016-12-01"
)

# Temporary
with open('faq.json') as page:
    page_json = json.load(page)
    print page_json

# Git/Gerrit FAQ id: 11010117
r = requests.get('https://confluence.cpqd.com.br/rest/api/content/11010117/child/page',
                 auth=HTTPBasicAuth('jsiloto', '$pwx=ad9'))

for child in r.json()['results']:
    page = child['_links']['self']
    page = page + '?expand=body.storage'
    p = requests.get(page, auth=HTTPBasicAuth('jsiloto', '$pwx=ad9'))
    p = {'page': page, 'content': p.json()['body']['storage']['value']}
    with open(child['id']+'.json', 'w+') as fp:
        json.dump(p, fp);
        add_doc = discovery.add_document('2fe9a94b-4655-4547-a179-896176b4bbf8', 'b2578d25-876c-412a-ae5f-1e562648f446', file_info=fp)
        print(json.dumps(add_doc, indent=2))