import json
import logging
import os
from .serializers import RateListSerializer

# Some basic logging
log = logging.getLogger(__name__)

# Tells the application which file to use to load the initial rates
os.environ.setdefault('RATES_FILE', os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'rates.json'))


class RateDAO(object):
    def __init__(self):
        self.counter = 0
        self.rates = []

    def get(self, rate_id):
        for rate in self.rates:
            if rate['id'] == rate_id:
                return rate
        return None

    def create(self, data):
        rate = data
        self.counter = self.counter + 1
        rate['id'] = self.counter
        self.rates.append(rate)
        return rate

    def delete(self, rate_id):
        rate = self.get(rate_id)
        self.rates.remove(rate)

    def drop(self):
        self.rates = []
        log.info("Dropped all the existing rates")

    def load_data_from_file(self, file_path):
        try:
            with open(file_path) as rates_file:
                raw_rates = json.loads(rates_file.read())
                serializer = RateListSerializer(data = raw_rates)

                if serializer.is_valid():
                    for item in serializer.validated_data['rates']:
                        self.create(item)
        except Exception as e:
            log.error("Unable to retrieve rates from specified file: {}".format(file_path))
            log.error("Error: {}".format(e.__str__()))


# Initializes an in memory data access object for the rates
DAO = RateDAO()
DAO.load_data_from_file(os.environ.get('RATES_FILE'))
