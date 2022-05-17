from django.urls import path, include

# what does router do?
# it automatically creates different urls in order to
# list all elements in a viewset
from rest_framework.routers import DefaultRouter

from recipe import views

# register our view with our router
router = DefaultRouter()
router.register("ingredients", views.IngredientViewSet)
router.register("tags", views.TagViewSet)
router.register("recipes", views.RecipeViewSet)

app_name = "recipe"

urlpatterns = [
    path("", include(router.urls))  # including all urls created by the router
]
