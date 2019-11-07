from django.urls import path
from .views import RateList, RateDetail, RatePrice

urlpatterns = [
    path('bulk', RateList.as_view(), name='rate-list'),
    path('price', RatePrice.as_view(), name='rate-price'),
]
