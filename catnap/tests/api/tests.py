"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse


USERNAME = 'alex'
PASSWORD = 'f'

class RestResourcesIntegrationsTest(TestCase):
    fixtures = ['testdata.json']

    def setUp(self):
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_entry_point(self):
        res = self.client.get(reverse('api-entry_point'))
        self.assertEqual(res.status_code, 200)

    def test_deck_list(self):
        res = self.client.get(reverse('api-deck_list'))
        self.assertEqual(res.status_code, 200)


        
