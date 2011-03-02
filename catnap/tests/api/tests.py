"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from models import Deck
from restresources import DeckResource, UserResource
from catnap.restresources import RestModelResource

USERNAME = 'alex'
PASSWORD = 'f'

def res_to_json(http_res):
    return json.loads(http_res.content)
    

class RestResourceIntegrationsTest(TestCase):
    fixtures = ['testdata.json']

    def setUp(self):
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_entry_point(self):
        res = self.client.get(reverse('api-entry_point'))
        self.assertEqual(res.status_code, 200)

        data = res_to_json(res)
        self.assertTrue('deck_list_url' in data.keys())
        self.assertEqual(data['deck_list_url'], reverse('api-deck_list'))

    def test_deck_list(self):
        res = self.client.get(reverse('api-deck_list'))
        self.assertEqual(res.status_code, 200)

        data = res_to_json(res)
        self.assertTrue('deck_list' in data.keys())
        deck_list = data['deck_list']
        self.assertTrue(len(deck_list) >= 1)
        self.assertTrue('name' in deck_list[0].keys())

        owner = deck_list[0]['owner']
        self.assertTrue('password' not in owner.keys())


class RestResourcesTest(TestCase):
    fixtures = ['testdata.json']

    def test_deck_resource(self):
        deck = Deck.objects.get(id=1)
        resource = DeckResource(deck)



        
