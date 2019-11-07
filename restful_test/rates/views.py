from .models import DAO
from .serializers import RateSerializer, RateListSerializer
from rest_framework import response, status, generics, serializers
from drf_yasg.utils import swagger_auto_schema, swagger_serializer_method
from drf_yasg import openapi

import dateutil.parser
import logging

# Some basic logging to help with debugging
log = logging.getLogger(__file__)


class RateList(generics.GenericAPIView):
    serializer_class = RateListSerializer
    """
    Rates list management.
    """
    def get(self, request, format=None):
        """
        Return a list of all rates.
        """
        rates_object = {'rates': DAO.rates}
        serializer = self.get_serializer(rates_object)
        return response.Response(data=serializer.data)

    def post(self, request, format=None):
        """
        Replace the current rates with a new set of rates, return a new json object representing the rates
        and their assigned new id for each entry
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            DAO.drop()
            for item in serializer.validated_data['rates']:
                DAO.create(item)

            rates_object = {'rates': DAO.rates}
            serializer = self.get_serializer(rates_object)
            return response.Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class RateDetail(generics.GenericAPIView):
    serializer_class = RateSerializer
    """
    Retrieve, rate instance.
    """
    def get_queryset(self):
        return DAO.rates

    def get(self, request, pk, format=None):
        rate = DAO.get(rate_id=pk)
        if rate is None:
            return response.Response(status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(rate)
        return response.Response(serializer.data)


class RatePrice(generics.GenericAPIView):
    start_dt_param = openapi.Parameter(
        'start_dt',
        openapi.IN_QUERY,
        description="Start DateTime",
        type=openapi.TYPE_STRING)
    end_dt_param = openapi.Parameter(
        'end_dt',
        openapi.IN_QUERY,
        description="End DateTime",
        type=openapi.TYPE_STRING)

    unavailable_response = openapi.Response(
        'The price is unavailable, "unavailable" is returned',
        schema=openapi.Schema(type=openapi.TYPE_STRING)
    )
    price_response = openapi.Response(
        'The selected rate price in integer format',
        schema=openapi.Schema(type=openapi.TYPE_INTEGER,),
    )

    @swagger_auto_schema(
        manual_parameters=[start_dt_param, end_dt_param],
        responses={
            200: price_response,
            404: unavailable_response
        }
    )
    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get(self, request, format=None):
        start_dt = dateutil.parser.parse(request.query_params['start_dt'])
        end_dt = dateutil.parser.parse(request.query_params['end_dt'])

        valid_rates = []
        for rate in DAO.rates:
            loc_start = start_dt.astimezone(tz=rate['tz'])
            loc_end = end_dt.astimezone(tz=rate['tz'])

            # Make sure the rate requested does not span multiple days
            if loc_start.weekday() != loc_end.weekday():
                return response.Response(status=status.HTTP_404_NOT_FOUND,data='unavailable')

            # Filter out only the rates which apply to the current local day
            if not loc_start.weekday() in rate['days']:
                continue

            if not rate['times'][0] <= loc_start.time():
                continue

            if not rate['times'][1] >= loc_end.time():
                continue
            valid_rates.append(rate)

        # Rate unavailable return the answer in the required format
        if len(valid_rates) == 0:
            return response.Response(status=status.HTTP_404_NOT_FOUND, data='unavailable')

        # Multiple rates found, return an internal server error
        if len(valid_rates) > 1:
            return response.Response(status=status.HTTP_404_NOT_FOUND, data='unavailable')

        # Correct Answer
        return response.Response(valid_rates[0]['price'])
