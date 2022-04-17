# to get the right view
from rest_framework import viewsets, mixins
# to authenticate the request
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from recipe import serializers

# mixins allow us to specify exactly what the endpoint will be able to do
class TagViewSet(viewsets.GenericViewSet, 
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # notice how the current user can be retrieved from the request attribute!
        return super().get_queryset().filter(user=self.request.user).order_by("-name")
    
    def perform_create(self, serializer):
        """Create a new tag, hooking in the create process"""
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the database"""
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """Return objects only for the currently authenticated user"""
        return super().get_queryset().filter(user=self.request.user).order_by("-name")
    
    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)
    