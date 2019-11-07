"""restful_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

swagger_info = openapi.Info(
    title='Rates API',
    default_version='v1',
    description="Demo project for parking rates retrieval",
    terms_of_service='https://www.google.com/policies/terms/',
    contact=openapi.Contact(email='bartei81@gmail.com'),
    license=openapi.License(name="MIT License"),
)


SchemaView = get_schema_view(
    info=swagger_info,
    validators=['flex'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', SchemaView.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('rate/', include('rates.urls')),
]
