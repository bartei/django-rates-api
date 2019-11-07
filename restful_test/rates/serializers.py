from rest_framework import serializers
from rest_framework.fields import Field, empty
from rest_framework.exceptions import ValidationError

import datetime
import pytz
import logging

log = logging.getLogger(__file__)

weekdays = {
    'mon': 0,
    'tues': 1,
    'wed': 2,
    'thurs': 3,
    'fri': 4,
    'sat': 5,
    'sun': 6,
}

inv_weekdays = dict((v, k) for k, v in weekdays.items())


class TimeZoneField(Field):
    initial = pytz.timezone('UTC')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run_validation(self, data=empty):
        # Extract timezone and perform sanity checks
        try:
            timezone = pytz.timezone(data)
            log.info("Identified timezone as: {}".format(timezone.zone))
        except Exception as e:
            log.error("Error parsing given timezone: {}".format(data))
            log.debug("Error message: {}".format(e.__str__()))
            raise ValidationError

        return super().run_validation(data)

    def to_internal_value(self, data):
        try:
            value = pytz.timezone(data)
        except Exception as e:
            self.fail('invalid: {}'.format(e.__str__()))
        return value

    def to_representation(self, value):
        return value.zone


class WeekDayField(serializers.Field):
    initial = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run_validation(self, data=empty):
        try:
            if data[-1] != ",":
                data = "{},".format(data)

            days_list = data.split(",")[:-1]

            # Make sure the names are correct
            malformed_days = [item for item in days_list if item not in weekdays]
            if len(malformed_days) > 0:
                raise ValidationError
        except Exception as e:
            raise ValidationError

        return super().run_validation(data)

    def to_internal_value(self, data):
        if data[-1] != ",":
            data = "{},".format(data)

        days_list = data.split(",")[:-1]
        value = [weekdays[item] for item in days_list]
        return value

    def to_representation(self, value):
        names_list = [inv_weekdays[item] for item in value]
        return ",".join(names_list)


class TimeRangeField(serializers.Field):
    initial = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run_validation(self, data=empty):
        # Extract start-end datetime and perform some data sanity checks
        if not isinstance(data, str):
            raise ValidationError

        try:
            start_time_str, end_time_str = data.split("-")
        except Exception as e:
            log.error("Error validating TimeRangeField: {}".format(e.__str__()))
            raise ValidationError

        if len(start_time_str) != 4:
            raise ValidationError

        if len(end_time_str) != 4:
            raise ValidationError

        return super().run_validation(data)

    def to_internal_value(self, data):
        try:
            start_time_str, end_time_str = data.split("-")

            value = list()
            value.append(datetime.time(
                hour=int(start_time_str[0:2]),
                minute=int(start_time_str[2:4]),
                second=00,
            ))
            value.append(datetime.time(
                hour=int(end_time_str[0:2]),
                minute=int(end_time_str[2:4]),
                second=00,
            ))
        except Exception as e:
            log.error("Error: {}".format(e.__str__()))
            raise

        return value

    def to_representation(self, value):
        return "{}-{}".format(
            value[0].strftime("%H%M"),
            value[1].strftime("%H%M")
        )


class RateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    times = TimeRangeField()
    tz = TimeZoneField()
    days = WeekDayField()
    price = serializers.IntegerField()


class RateListSerializer(serializers.Serializer):
    rates = RateSerializer(many=True)
