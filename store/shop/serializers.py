from rest_framework import serializers
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,\
    ProductImage,OrderItem,Basket,Profile,Address,ReceiverInformation,Province

from django.db.models.aggregates import Min,Max,Avg,Sum

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image','product']

class ProductSerializer(serializers.ModelSerializer):
    image = ImageSerializer(many=True,read_only=True)
    price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    new_price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id','name','description','info','image','category','price','stock','rate','discount','new_price','updated']
        read_only_fields = ['id','price','stock','rate','discount','new_price','updated']
        wrire_only_fields = ['category','description','info']

    def get_rate(self,instance):
        rate = instance.rates.all().aggregate(avg=Avg('rate'))
        return rate['avg']

    def get_stock(self,instance):
        stock = instance.variations.all().aggregate(stock=Sum('stock'))
        return stock['stock']

    def get_price(self,instance):
        price = instance.variations.all().aggregate(min_price=Min('price'))
        return price['min_price']

    def get_discount(self,instance):
        # discount = instance.variations.all().aggregate(Min('price')).discount
        discount = instance.variations.get(price =instance.variations.all().aggregate(min_price=Min('price'))['min_price']).discount

        return discount

    def get_new_price(self,instance):
        old_price = self.get_price
        discount = self.get_discount
        new_price = None
        if discount is not None:
            new_price = old_price - (discount * old_price // 100)
        return new_price
        
