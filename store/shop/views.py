from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,\
    ProductImage,OrderItem,Basket,Profile,Address,ReceiverInformation,Province

# Create your views here.
    


class ProductList(ListCreateAPIView):

    def get_queryset(self):
        return Product.objects.all()

    def get_serializer_class(self):
        return 