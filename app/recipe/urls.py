from django.urls import path, include
# what does it do? automatically will create different urls in order to list all elements in a viewset
from rest_framework.routers import DefaultRouter

from recipe import views

# register our view with our router
router = DefaultRouter()
router.register('tags', views.TagViewSet)


app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))  # including all urls created by the router
]

