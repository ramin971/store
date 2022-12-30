from django.shortcuts import render
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,\
    ProductImage,OrderItem,Basket,Profile,Address,ReceiverInformation,Province
from .serializers import ProductSerializer
import json
# Create your views here.
    


class ProductList(ListCreateAPIView):
    # parser_classes = [JSONParser]
    parser_classes = [MultiPartParser,FormParser]

    def get_queryset(self):
        return Product.objects.all()

    def get_serializer_class(self):
        return ProductSerializer

    def get_serializer_context(self):
        return {'request':self.request}

    # def create(self, request, *args, **kwargs):
    #     request.data._mutable = True
    #     variations=request.data.pop('variations')
    #     json_variations=json.loads(variations)
    #     request.data['variations']=json_variations
    #     # request.data=JSONRenderer().render(request.data)
    #     super().create(request, *args, **kwargs)