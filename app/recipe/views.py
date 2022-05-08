# to create custom actions
from rest_framework.decorators import action
from rest_framework.response import Response
# to get the right view
from rest_framework import viewsets, mixins, status
# to authenticate the request
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe import serializers

# mixins allow us to specify exactly what the endpoint will be able to do
class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by("-name")
    
    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)
    


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-title")
    
    def get_serializer_class(self):
        """Return different serializer class depending on url"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe"""
        # assigning authenticated user
        serializer.save(user=self.request.user)
    
    # detail=True, use detail url (with id); pk None means using default id?
    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        # based on ID
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=self.request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )



    

