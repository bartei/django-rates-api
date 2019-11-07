from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import logging


log = logging.getLogger(__file__)


class AccountTests(APITestCase):
    def test_available_rate_1(self):
        url = reverse('rate-price')
        parameters = {
            'start_dt': '2015-07-01T07:00:00-05:00',
            'end_dt': '2015-07-01T12:00:00-05:00'
        }
        log.info("Checking available rate 1")
        response = self.client.get(url, data=parameters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 1750)

    def test_available_rate_2(self):
        url = reverse('rate-price')
        parameters = {
            'start_dt': '2015-07-04T15:00:00+00:00',
            'end_dt': '2015-07-04T20:00:00+00:00'
        }
        log.info("Checking available rate 2")
        response = self.client.get(url, data=parameters)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 2000)

    def test_unavailable_rate_1(self):
        url = reverse('rate-price')
        parameters = {
            'start_dt': '2015-07-04T07:00:00+05:00',
            'end_dt': '2015-07-04T20:00:00+05:00'
        }
        log.info("Checking unavailable rate 1")
        response = self.client.get(url, data=parameters)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, "unavailable")

    def test_unavailable_rate_2(self):
        url = reverse('rate-price')
        parameters = {
            'start_dt': '2015-07-04T15:00:00+00:00',
            'end_dt': '2015-07-05T20:00:00+00:00'
        }
        log.info("Checking unavailable rate 1, going over 1 day")
        response = self.client.get(url, data=parameters)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, "unavailable")

    def test_read_bulk_rates(self):
        url = reverse('rate-list')
        log.info("Checking bulk rate retrieval")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(member='rates', container=response.data)
        self.assertEqual(len(response.data['rates']), 5)

    def test_write_bulk_rates(self):
        test_data = {
            "rates": [
                {
                    "days": "mon,tues,sun",
                    "times": "1000-2000",
                    "tz": "Europe/Rome",
                    "price": 1500
                },
                {
                    "days": "fri,sat,mon",
                    "times": "0900-2100",
                    "tz": "America/Chicago",
                    "price": 20000
                },
            ]
        }
        log.info("Checking bulk rate update")
        url = reverse('rate-list')
        response = self.client.post(path=url, data=test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(member='rates', container=response.data)
        self.assertEqual(len(response.data['rates']), 2)
