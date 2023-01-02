from rest_framework import serializers
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,\
    ProductImage,OrderItem,Basket,Profile,Address,ReceiverInformation,Province

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models.aggregates import Min,Max,Avg,Sum
import json
from rest_framework.exceptions import ValidationError

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image','product']

class InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Info
        # fields = ['id','value']
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    full_path=serializers.SerializerMethodField()
    parent=serializers.CharField(write_only=True,max_length=50,allow_blank=True)
    class Meta:
        model = Category
        fields = ['id','name','parent','full_path']
        # fields = ['id','name','parent']

        read_only_fields = ['id','full_path']
        # extra_kwargs={'parent':{'write_only':True}}

    def create(self, validated_data):
        parent_name = validated_data.pop('parent')
        if parent_name:
            parent=get_object_or_404(Category,name=parent_name)
            category=Category.objects.create(parent=parent,**validated_data)
        else:
            category=Category.objects.create(parent=None,**validated_data)
        return category

    def get_full_path(self,instance):
        return instance.__str__()

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

class VariationSerializer(serializers.ModelSerializer):
    # color = ColorSerializer()
    color = serializers.CharField(write_only=True)
    # size = SizeSerializer(many=True)
    size = serializers.ListField(child=serializers.CharField(max_length=2),write_only=True)
    class Meta:
        model = Variation
        fields = ['id','color','size','price','discount','stock','updated']
        read_only_fields = ['id','updated']
    #  currently not used (bellow)
    def create(self, validated_data):
        color_data = validated_data.pop('color')
        # print('****color=',color_data)
        sizes_data = validated_data.pop('size')
        # print('#####size=',sizes_data)
        # product_data = validated_data.pop('product_id')
        # product = Product.objects.get(pk=product_data)
        # product = get_object_or_404(Product,pk=product_data)
        color = Color.objects.get_or_create(value=color_data)
        variation = Variation.objects.create(color=color,**validated_data)
        for size_data in sizes_data:
            size = Size.objects.get_or_create(value=str(**size_data))
            variation.size.add(size)
        return variation
        

class ProductSerializer(serializers.ModelSerializer):
    # images = ImageSerializer(many=True,write_only=True)
    # create image_list view and then try:
    # fffffffuck 
    image = serializers.SerializerMethodField(read_only=True)
    images= serializers.ListField(child=serializers.ImageField(max_length=512000),write_only=True)

    # info = InfoSerializer(many=True,write_only=True)
    # ################
    info = serializers.ListField(child=serializers.CharField(max_length=300),allow_empty=True,write_only=True)
    # info = serializers.CharField(allow_blank=True)
    # info = serializers.JSONField(write_only=True)

    # category = CategorySerializer(write_only=True)
    # category = serializers.StringRelatedField()
    category = serializers.CharField(write_only=True,max_length=50)
    # variations=VariationSerializer(many=True,read_only=True)
    variations = serializers.JSONField(write_only=True)
    price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    new_price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()

    def validate_variations(self,value):
        if not isinstance(value,list):
            ValidationError("variation expect a list of dictionary")

        for item in value:
            serializer = VariationSerializer(data=item)
            serializer.is_valid(raise_exception=True)
        return value

    class Meta:
        model = Product
        # add images to fields*********************************************
        fields = ['id','name','description','info','category','image','images','variations','price','stock','rate','discount','new_price','updated']
        read_only_fields = ['id','price','stock','rate','discount','new_price','updated']
        extra_kwargs={'description':{'write_only':True}}

    @transaction.atomic()
    def create(self, validated_data):
        category_data = validated_data.pop('category')
        # category=Category.objects.get(name=category_data)
        category = get_object_or_404(Category,name=category_data)
        infos_data = validated_data.pop('info')
        # infos_data_json = json.loads(infos_data)
        images_data = validated_data.pop('images')
        variations_data = validated_data.pop('variations')
    
        product = Product.objects.create(category=category,**validated_data)
        
        for image_data in images_data:
            ProductImage.objects.create(product=product,image=image_data)
        # print('infos data type=',type(infos_data))
        infos=json.loads(infos_data[0])
        # print(infos,type(infos))

        for info_data in infos:
            info,_ = Info.objects.get_or_create(value=info_data)
            product.info.add(info)

        for variation_data in variations_data:
            color=variation_data.pop('color')
            print('color$',color)
            temp_color,_ = Color.objects.get_or_create(value=color)
            sizes=variation_data.pop('size')
            variation=Variation.objects.create(product=product,color=temp_color,**variation_data)
            print('sizes$$',sizes)
            for size in sizes:
                temp_size,_ = Size.objects.get_or_create(value=size)
                variation.size.add(temp_size)
        return product

    # def get_var(self,instance):
    #     variation=instance.variations.all()
    #     return variation

    def get_image(self,obj):
        request = self.context.get('request')
        image = request.build_absolute_uri(obj.images.first().image.url)
        # images= [request.build_absolute_uri(i.image.url) for i in obj.images.all()]
        return image

    def get_rate(self,instance):
        rate = instance.rates.all().aggregate(avg=Avg('rate'))
        return rate['avg']

    def get_stock(self,instance):
        stock = instance.variations.all().aggregate(stock=Sum('stock'))
        # stock = self.get_var(instance=instance).aggregate(stock=Sum('stock'))

        return stock['stock']

    def get_price(self,instance):
        price = instance.variations.all().aggregate(min_price=Min('price'))
        # price = self.get_var(instance=instance).aggregate(min_price=Min('price'))

        return price['min_price']

    def get_discount(self,instance):
        # discount = instance.variations.all().aggregate(Min('price')).discount
        discount = instance.variations.get(price =self.get_price(instance)).discount
        return discount

    def get_new_price(self,instance):
        # print('@@@ ', self.get_price(instance))
        # print('@@@ ', type(self.get_price(instance)))

        old_price = self.get_price(instance)
        discount = self.get_discount(instance)
        if discount is not None:
            new_price = old_price - (discount * old_price // 100)
            return new_price
        return old_price
        
# class