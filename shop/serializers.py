from rest_framework import serializers
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,\
    ProductImage,OrderItem,Basket,Profile,Address,ReceiverInformation,Province,Coupon

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models.aggregates import Min,Max,Avg,Sum
import json
import uuid
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

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id','product','user','rate']
        read_only_fields=['id','user']

    def create(self, validated_data):
        print('####################')
        print('@@@@@@@@@@',validated_data)
        user = self.context.get('user')
        print('user',user)
        validated_data['user'] = user
        # self.user = user
        return super(RatingSerializer,self).create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id','user','user_name','product','text',]
        read_only_fields=['id','user','user_name']

    def create(self, validated_data):
        user = self.context.get('user')
        validated_data['user'] = user
        return super(CommentSerializer,self).create(validated_data)

    def get_user_name(self,instance):
        user_name = instance.user.username
        return user_name

class CategorySerializer(serializers.ModelSerializer):
    full_path=serializers.SerializerMethodField(read_only=True)
    # if you want use name-of-parent, must define create and update method as bellow 
    # parent=serializers.CharField(write_only=True,max_length=50,allow_blank=True)
    products_count=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Category
        fields = ['id','name','parent','products_count','full_path']
        read_only_fields = ['id','full_path','products_count']
    

    # def create(self, validated_data):
    #     # print('####################################')
    #     parent_name = validated_data.pop('parent')
    #     if parent_name:
    #         parent=get_object_or_404(Category,name=parent_name)
    #         category=Category.objects.create(parent=parent,**validated_data)
    #     else:
    #         category=Category.objects.create(parent=None,**validated_data)
    #     return category

    # def update(self, instance, validated_data):
    #     # print('@@@@@@@@@@',validated_data)
    #     if 'parent' in validated_data:
    #         parent_name = validated_data.pop('parent')
    #         if parent_name:
    #             parent = get_object_or_404(Category,name=parent_name)
    #             instance.parent = parent
    #         else:
    #             instance.parent = None
    #         # print('!!!!!!!!!!!!!!!!!!!!!!')


    #     return super(CategorySerializer,self).update(instance, validated_data)

    def get_full_path(self,instance):
        return instance.__str__()
    
    def get_products_count(self,instance):
        # p_count=instance.products.count()
        return instance.products_count

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

# original
class VariationSerializer(serializers.ModelSerializer):
    # color = ColorSerializer()
    color = serializers.CharField()
    # size = SizeSerializer(many=True)
    size = serializers.CharField()
    # size = serializers.ListField(child=serializers.CharField(max_length=2),source='size.all')
    class Meta:
        model = Variation
        fields = ['id','color','size','price','discount','stock','updated']
        read_only_fields = ['id','updated']
    #  currently not used (bellow)
    def create(self, validated_data):
        print('#####variation-serializer create')
        color_data = validated_data.pop('color')
        size_data = validated_data.pop('size')
        color,_ = Color.objects.get_or_create(value=color_data)
        size,_ = Size.objects.get_or_create(value=str(size_data))
        variation = Variation.objects.create(color=color,size=size,**validated_data)
        
        return variation

# class VariationSerializer(serializers.ModelSerializer):
#     # color = ColorSerializer()
#     color = serializers.CharField()
#     # size = SizeSerializer(many=True)
#     size = serializers.ListField(child=serializers.CharField(max_length=2),source='size.all')
#     class Meta:
#         model = Variation
#         fields = ['id','color','size','price','discount','stock','updated']
#         read_only_fields = ['id','updated']
#     #  currently not used (bellow)
#     # def create(self, validated_data):
#     #     color_data = validated_data.pop('color')
#     #     # print('****color=',color_data)
#     #     sizes_data = validated_data.pop('size')
#     #     # print('#####size=',sizes_data)
#     #     # product_data = validated_data.pop('product_id')
#     #     # product = Product.objects.get(pk=product_data)
#     #     # product = get_object_or_404(Product,pk=product_data)
#     #     color = Color.objects.get_or_create(value=color_data)
#     #     variation = Variation.objects.create(color=color,**validated_data)
#     #     for size_data in sizes_data:
#     #         size = Size.objects.get_or_create(value=str(**size_data))
#     #         variation.size.add(size)
#     #     return variation

#     # def get_color(self,instance):
#     #     color = instance.values('color')
#     #     print('#########color:',color)
#     #     return color
    
#     def get_sizes(self,instance):
#         size = instance.values('size')
#         print('#########size:',size)
#         return size    

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    info = InfoSerializer(many=True)
    variations=VariationSerializer(many=True)
    price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    new_price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id','name','description','info','category','image','variations','price','stock','rate','discount','new_price','updated']
        read_only_fields = ['id','price','stock','rate','discount','new_price','updated']
        extra_kwargs={'description':{'write_only':True}}

    @transaction.atomic()
    def create(self, validated_data):
        infos_data = validated_data.pop('info')
        variations_data = validated_data.pop('variations')
        product = Product.objects.create(**validated_data) 

        for info_data in infos_data:
            info_value = info_data.get('value')
            info,_ = Info.objects.get_or_create(value=info_value)
            product.info.add(info)

        for variation_data in variations_data:
            color=variation_data.pop('color')
            temp_color,_ = Color.objects.get_or_create(value=color)
            size=variation_data.pop('size')
            temp_size,_ = Size.objects.get_or_create(value=size)

            variation=Variation.objects.create(product=product,color=temp_color,size=temp_size,**variation_data)
            
        return product

    

    def get_image(self,obj):
        request = self.context.get('request')
        try:
            image = request.build_absolute_uri(obj.images.first().image.url)
        except:
            image = None
        # images= [request.build_absolute_uri(i.image.url) for i in obj.images.all()]
        return image

    # def get_rate(self,instance):
    #     rate = instance.rates.all().aggregate(avg=Avg('rate'))
    #     return rate['avg']
    def get_rate(self,instance):
        rate = instance.avg_rate
        return rate


    # def get_stock(self,instance):
    #     stock = instance.variations.all().aggregate(stock=Sum('stock'))
    #     return stock['stock']
    def get_stock(self,instance):
        stock = instance.stock
        return stock
    

    # def get_price(self,instance):
    #     price = instance.variations.all().aggregate(min_price=Min('price'))
    #     return price['min_price']
    def get_price(self,instance):
        price = instance.price
        return price


    def get_discount(self,instance):
        try:
            discount = instance.variations.get(price =self.get_price(instance)).discount
        except Variation.MultipleObjectsReturned:
            discount = instance.variations.filter(price =self.get_price(instance)).aggregate(max_discount=Max('discount'))['max_discount']
        return discount


    def get_new_price(self,instance):
        old_price = self.get_price(instance)
        discount = self.get_discount(instance)
        if discount is not None:
            new_price = old_price - (discount * old_price // 100)
            return new_price
        return old_price


class ProductDetailSerializer(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField(read_only=True)
    info = InfoSerializer(many=True)
    # add paginated-comments to views/ProductDetail get method
    # comments = CommentSerializer(many=True,read_only=True)###############
    variations = VariationSerializer(many=True)
    add_variations = serializers.BooleanField(write_only=True,default=True)

    class Meta:
        model = Product
        fields = ['id','name','slug','category','rate','description','info','image','variations','add_variations']
        read_only_fields = ['id','slug','rate','comments']

    def update(self, instance, validated_data):

        infos_data = validated_data.get('info')
        variations_data = validated_data.get('variations')
        add = validated_data.pop('add_variations')
     
        if infos_data:
            validated_data.pop('info')
            instance.info.clear()
        
            for info_data in infos_data:
                info_value = info_data.get('value')
                info,_ =Info.objects.get_or_create(value=info_value)
                instance.info.add(info)

        if variations_data:
            validated_data.pop('variations')
            if not add:
                instance.variations.all().delete()
            for variation_data in variations_data:
                color = variation_data.pop('color')
                temp_color,_ = Color.objects.get_or_create(value=color)
                size = variation_data.pop('size')
                temp_size,_ = Size.objects.get_or_create(value=size)
                Variation.objects.create(product=instance,color=temp_color,size=temp_size,**variation_data)

        return super(ProductDetailSerializer,self).update(instance, validated_data)


    def get_rate(self,instance):
        rate = instance.avg_rate
        return rate

    def get_image(self,instance):
        request = self.context.get('request')
        # images = instance.images.values()
        images= [request.build_absolute_uri(i.image.url) for i in instance.images.all()]
        return images

# ))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
# class ProductSerializer(serializers.ModelSerializer):
#     # images = ImageSerializer(many=True,write_only=True)
#     # create image_list view and then try:
#     # fffffffuck 
#     image = serializers.SerializerMethodField(read_only=True)
#     images= serializers.ListField(child=serializers.ImageField(max_length=512000),write_only=True)

#     # info = InfoSerializer(many=True,write_only=True)
#     # ################
#     info = serializers.ListField(child=serializers.CharField(max_length=300),allow_empty=True,write_only=True)
#     # info = serializers.CharField(allow_blank=True)
#     # info = serializers.JSONField(write_only=True)

#     # if you want use name-of-parent, must uncomment #########  
#     # category = serializers.CharField(write_only=True,max_length=50) ##########
#     # variations=VariationSerializer(many=True,read_only=True)
#     variations = serializers.JSONField(write_only=True)
#     price = serializers.SerializerMethodField()
#     discount = serializers.SerializerMethodField()
#     new_price = serializers.SerializerMethodField()
#     stock = serializers.SerializerMethodField()
#     rate = serializers.SerializerMethodField()

#     def validate_variations(self,value):
#         if not isinstance(value,list):
#             ValidationError("variation expect a list of dictionary")

#         for item in value:
#             serializer = VariationSerializer(data=item)
#             serializer.is_valid(raise_exception=True)
#         return value

#     # def to_representation(self, instance):
#     #     ret=super(ProductSerializer,self).to_representation(instance)
#     #     ret['price']=instance.variations.all().aggregate(min_price=Min('price'))['min_price']
#     #     return ret

#     class Meta:
#         model = Product
#         fields = ['id','name','description','info','category','image','images','variations','price','stock','rate','discount','new_price','updated']
#         read_only_fields = ['id','price','stock','rate','discount','new_price','updated']
#         extra_kwargs={'description':{'write_only':True}}

#     @transaction.atomic()
#     def create(self, validated_data):
#         # category_data = validated_data.pop('category') ########
#         # category=Category.objects.get(name=category_data)
#         # category = get_object_or_404(Category,name=category_data) #########
#         infos_data = validated_data.pop('info')
#         # infos_data_json = json.loads(infos_data)
#         images_data = validated_data.pop('images')
#         variations_data = validated_data.pop('variations')
#         # print('variations-data#####',variations_data)
    
#         # product = Product.objects.create(category=category,**validated_data) ########
#         product = Product.objects.create(**validated_data) 

        
#         for image_data in images_data:
#             ProductImage.objects.create(product=product,image=image_data)
#         # print('infos data type=',type(infos_data))
#         infos=json.loads(infos_data[0])
#         # print(infos,type(infos))

#         for info_data in infos:
#             info,_ = Info.objects.get_or_create(value=info_data)
#             product.info.add(info)

#         for variation_data in variations_data:
#             # print('variation#####',variation_data)

#             color=variation_data.pop('color')
#             # print('color$',color)
#             temp_color,_ = Color.objects.get_or_create(value=color)
#             size=variation_data.pop('size')
#             temp_size,_ = Size.objects.get_or_create(value=size)
#             # print('variation@@@@@@@',variation_data)
#             # print('variation*****',**variation_data)


#             variation=Variation.objects.create(product=product,color=temp_color,size=temp_size,**variation_data)
#             # print('sizes$$',sizes)
#             # for size in sizes:
#                 # temp_size,_ = Size.objects.get_or_create(value=size)
#                 # variation.size.add(temp_size)
#             # print('variation',variation)
#         # product = product.annotate(avg_rate=Avg('rates__rate')
#         # ,stock=Sum('variations__stock'),price=Min('variations__price'))
#         return product

    

#     def get_image(self,obj):
#         request = self.context.get('request')
#         image = request.build_absolute_uri(obj.images.first().image.url)
#         # images= [request.build_absolute_uri(i.image.url) for i in obj.images.all()]
#         return image

#     # def get_rate(self,instance):
#     #     rate = instance.rates.all().aggregate(avg=Avg('rate'))
#     #     return rate['avg']
#     def get_rate(self,instance):
#         rate = instance.avg_rate
#         return rate


#     # def get_stock(self,instance):
#     #     stock = instance.variations.all().aggregate(stock=Sum('stock'))
#     #     return stock['stock']
#     def get_stock(self,instance):
#         stock = instance.stock
#         return stock
    

#     # def get_price(self,instance):
#     #     price = instance.variations.all().aggregate(min_price=Min('price'))
#     #     return price['min_price']
#     # 88888888888888888888888888888888888888
#     def get_price(self,instance):
#         price = instance.price
#         return price


#     def get_discount(self,instance):
#         # discount = instance.variations.all().aggregate(Min('price')).discount
#         discount = instance.variations.get(price =self.get_price(instance)).discount
#         return discount

#     def get_new_price(self,instance):
#         # print('@@@ ', self.get_price(instance))
#         # print('@@@ ', type(self.get_price(instance)))

#         old_price = self.get_price(instance)
#         discount = self.get_discount(instance)
#         if discount is not None:
#             new_price = old_price - (discount * old_price // 100)
#             return new_price
#         return old_price
# ))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
class AddImageSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(max_length=512000),write_only=True)
    add = serializers.BooleanField(write_only=True,default=True)
    class Meta:
        model = ProductImage
        fields = ['id','images','product','add']
        read_only_fields = ['id']

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        add = validated_data.pop('add')
        if not add:
            product = validated_data.get('product')
            product.images.all().delete()
        print('images:',images_data)
        for image_data in images_data:
            print('$$$$$$$########$$$$$')
            print('image:',image_data)
            image=ProductImage.objects.create(image=image_data,**validated_data)
        return image


# )))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
# class ProductDetailSerializer(serializers.ModelSerializer):
#     rate = serializers.SerializerMethodField()
#     image = serializers.SerializerMethodField(read_only=True)
#     images= serializers.ListField(child=serializers.ImageField(max_length=512000),write_only=True)
#     info = serializers.ListField(child=serializers.CharField(max_length=300),allow_empty=True,source='info.all')
#     # add paginated-comments to views/ProductDetail get method
#     # comments = CommentSerializer(many=True,read_only=True)###############
#     variations = VariationSerializer(many=True,read_only=True)
#     variation = serializers.JSONField(write_only=True)

#     class Meta:
#         model = Product
#         fields = ['id','name','slug','category','rate','description','info','image','images','variations','variation']
#         read_only_fields = ['id','slug','rate','comments']

#     def validate_variation(self,value):
#         if not isinstance(value,list):
#             ValidationError("variation expect a list of dictionary")

#         for item in value:
#             serializer = VariationSerializer(data=item)
#             serializer.is_valid(raise_exception=True)
#         return value

#     def update(self, instance, validated_data):
#         # can not use super because info,image,variations not normaly .they are list of things therfore needs to loop(get,pop)
#         # instance.name = validated_data.get('name',instance.name)
#         # instance.description = validated_data.get('description',instance.description)
#         # print('#########validated-data',validated_data)
#         infos_data = validated_data.get('info')
#         images_data = validated_data.get('images')
#         variations_data = validated_data.get('variation')
#         if infos_data:
#             # print('@@@@infos_data')
#             validated_data.pop('info')
#             instance.info.clear()
#             # print('####',infos_data.keys())
#             # print(type(infos_data['all'][0]))
#             # print('json**',type(json.loads(infos_data['all'][0])))
#             infos = json.loads(infos_data['all'][0])
#             # print('$$$$$$$$$ infos.json',infos)
#             for info_data in infos:
#                 info,_ =Info.objects.get_or_create(value=info_data)
#                 instance.info.add(info)

#         if images_data:
#             # print('@@@@images_data')
#             validated_data.pop('images')
#             instance.images.all().delete()
#             for image_data in images_data:
#                 ProductImage.objects.create(product=instance,image=image_data)

#         if variations_data:
#             # print('@@@@variations_data')
#             # print(type(variations_data))
#             validated_data.pop('variation')
#             instance.variations.all().delete()
#             # infos = json.loads(infos_data[0])
#             for variation_data in variations_data:
#                 color = variation_data.pop('color')
#                 temp_color,_ = Color.objects.get_or_create(value=color)
#                 size = variation_data.pop('size')
#                 temp_size,_ = Size.objects.get_or_create(value=size)
#                 variation = Variation.objects.create(product=instance,color=temp_color,size=temp_size,**variation_data)
#                 # for size in sizes:
#                     # temp_size,_ = Size.objects.get_or_create(value=size)
#                     # variation.size.add(temp_size)

#         # instance.save()
#         # return instance
#         # or remove name,description,.. and instead of instance.save write super.update(instance,validated_data) or instance.update

#         return super(ProductDetailSerializer,self).update(instance, validated_data)



#     def get_rate(self,instance):
#         rate = instance.avg_rate
#         return rate

#     def get_image(self,instance):
#         request = self.context.get('request')
#         # images = instance.images.values()
#         images= [request.build_absolute_uri(i.image.url) for i in instance.images.all()]
#         return images
# ))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
# class ProvinceSerializer(serializers.ModelSerializer):
#     province_choice = serializers.SerializerMethodField(read_only=True)
#     class Meta:
#         model = Province
#         fields = ['province_choice']

#     def get_province_choice(self,instance):
#         return Province.PROVINCE_CHOICES
        # return PROVINCE_CHOICES.__dict__.get('_display_map').get(instance['name'])

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
    
# class ProvinceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Province
#         fields='__all__'

class AddressSerializer(serializers.ModelSerializer):
    # province = ProvinceSerializer()
    province = serializers.CharField()

    class Meta:
        model = Address
        fields = ['id','province','full_address']
        read_only_fields = ['id','province']
    
    # def create(self, validated_data):
    #     print('################',validated_data)
    #     temp_province = validated_data.pop('province')
    #     # name = temp_province['name']
    #     print('name=',temp_province)
    #     province,_ = Province.objects.get_or_create(name__iexact=temp_province)
    #     address = Address.objects.create(province=province,**validated_data)
    #     return address



class ReceiverInformationSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    # province = ProvinceSerializer(write_only=True)
    class Meta:
        model = ReceiverInformation
        fields = ['id','full_name','national_code','phone','postal_code','address']
        read_only_fields = ['id']

    def create(self, validated_data):
        print('*********************',validated_data)
        # province_data = validated_data.pop('province')
        address_data = validated_data.pop('address')
        print('address.get(province)',address_data.get('province'))
        province_name = address_data.pop('province')
        province,_ = Province.objects.get_or_create(name__iexact=province_name)
        address = Address.objects.create(province=province,**address_data)
        receiver = ReceiverInformation.objects.create(address=address,**validated_data)
        return receiver

    def update(self, instance, validated_data):
        address_data = validated_data.get('address')
        if address_data:
            validated_data.pop('address')
            if instance.address is not None:
                instance.address.delete()
            province_name = address_data.pop('province')
            province,_ = Province.objects.get_or_create(name__iexact=province_name)
            address = Address.objects.create(province=province,**address_data)
            instance.address = address
        return super(ReceiverInformationSerializer,self).update(instance, validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    receiver = ReceiverInformationSerializer()
    class Meta:
        model = Profile
        fields = ['id','user','receiver','phone']
        read_only_fields = ['id','user']
    @transaction.atomic()
    def create(self, validated_data):
        user = self.context.get('user')
        validated_data['user'] = user
        receiver_data = validated_data.pop('receiver')
        receiver_serializer = ReceiverInformationSerializer(data=receiver_data)
        receiver_serializer.is_valid(raise_exception=True)
        receiver=receiver_serializer.save()
        # receiver,_ = ReceiverInformation.objects.get_or_create(**receiver_data)
        # print('####',receiver)

        profile = Profile.objects.create(receiver=receiver,**validated_data)
        return profile
        # return super(ProfileSerializer,self).create(validated_data)

    def update(self, instance, validated_data):
        receiver_data = validated_data.get('receiver')
        if receiver_data:
            validated_data.pop('receiver')
            if instance.receiver is not None:
                instance.receiver.delete()
            receiver_serializer = ReceiverInformationSerializer(data=receiver_data)
            receiver_serializer.is_valid(raise_exception=True)
            receiver=receiver_serializer.save()
            instance.receiver = receiver
            # profile = Profile.objects.create(receiver=receiver,**validated_data)
        return super(ProfileSerializer,self).update(instance, validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name']

class SimpleVariationSerializer(serializers.ModelSerializer):
    # color = ColorSerializer()
    color = serializers.CharField(read_only=True)
    # size = SizeSerializer(many=True)
    size = serializers.CharField(read_only=True)
    # size = serializers.ListField(child=serializers.CharField(max_length=2),source='size.all')
    product = SimpleProductSerializer(read_only=True)
    # product = serializers.CharField()
    class Meta:
        model = Variation
        fields = ['id','product','color','size','price','discount']
        read_only_fields = ['id','updated']


class AddOrderItemSerializer(serializers.ModelSerializer):
    # variation = VariationSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id','user','variation','quantity','basket']
        read_only_fields = ['id','user','basket']


    
    def create(self, validated_data):
        user = self.context.get('user')
        validated_data['user']=user
        # quantity = validated_data.pop('quantity')##########3##
        # validated_data['quantity']=1
        try:
            print('######## try1')
            temp_basket = Basket.objects.get(user=user,payment=False)
        except Basket.DoesNotExist:
            print('########except1')
            # print('******receiver=',user.profile.values(receiver))
            print('******receiver=',user.profile.receiver)
            try:
                print('######## try2')
                receiver=user.profile.receiver
            except :
                print('######## except2')
                raise NotFound('first complete your profile')
            # if receiver is not None:
            temp_basket = Basket.objects.create(user=user,receiver=receiver)
            print('##temp_basket',temp_basket)
        validated_data['basket']=temp_basket
        # now
        try:
            order_item = OrderItem.objects.get(basket=temp_basket,user=user,variation=validated_data['variation'])
            order_item.quantity += validated_data['quantity']
            print('1')
            print('########not created')
            order_item.save()
        except OrderItem.DoesNotExist:
            print('2')
            order_item = OrderItem.objects.create(**validated_data)
        print('######## order_item =',order_item)

        return order_item
    
    
   
class EditRemoveOrderItemSerializer(serializers.ModelSerializer):
    variation = SimpleVariationSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id','user','variation','quantity','basket']
        read_only_fields = ['id','user','basket']
    

class BasketSerializer(serializers.ModelSerializer):
    order_items = EditRemoveOrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Basket
        fields = ['id','user','tracking_code','ordered_date','payment','receiver','status','coupon','order_items','get_total_price']
        read_only_fields = ['id','user','tracking_code','ordered_date','payment','status','get_total_price']

    def create(self, validated_data):
        # #######################################################################
        # user = self.context.get('user')
        # try:
        #     receiver = user.profile.receiver
        # except: # work if receiver is null?
        #     raise ValueError('first complete your profile please!')
        print('##########user:',self.context.get('user'))
        validated_data['user'] = self.context.get('user')
        print('##########user:',validated_data.get('user'))
        return super(BasketSerializer,self).create(validated_data)

    def update(self, instance, validated_data):
        print('####validata',validated_data)
        if instance.payment:
            raise serializers.ValidationError('you have not access to change the basket that has been paid')
        was_paid = self.context.get('was_paid')
        if was_paid and (not instance.payment):
            print('&&&&&&&&&&&&&')
            instance.payment = True
            instance.ordered_date = timezone.now()
            instance.tracking_code = uuid.uuid4()
            return super(BasketSerializer,self).update(instance, validated_data)
        # if 'order_items' in validated_data:
        #     temp_order_items = validated_data.pop('order_items')
        #     instance.order_items.all().delete()
        #     for order_item_id in temp_order_items:
        #         # instance.order_items.add(order_item)
        #         order_item=OrderItem.objects.get(id=order_item_id)
        #         order_item.basket = instance
        return super(BasketSerializer,self).update(instance, validated_data)
        
    
# class AddToCartSerializer(serializers.ModelSerializer):
#     # variation = VariationSerializer(read_only=True)
#     class Meta:
#         model = OrderItem
#         fields = ['id','user','variation','quantity','basket']
#         read_only_fields = ['id','user','quantity','basket']
    
#     # def create(self, validated_data):
#     #     user = self.context.get('user')
#     #     validated_data['user']=user
#     #     return super(OrderItemSerializer,self).create(validated_data)
#     def create(self, validated_data):
#         user = self.context.get('user')
#         validated_data['user']=user
#         # validated_data['quantity']=1
#         try:
#             print('######## try1')
#             temp_basket = Basket.objects.get(user=user,payment=False)
#         except Basket.DoesNotExist:
#             print('########except1')
#             # print('******receiver=',user.profile.values(receiver))
#             print('******receiver=',user.profile.receiver)
#             try:
#                 print('######## try2')
#                 receiver=user.profile.receiver
#             except :
#                 print('######## except2')
#                 raise NotFound('first complete your profile')
#             # if receiver is not None:
#             temp_basket = Basket.objects.create(user=user,receiver=receiver)
#             print('##temp_basket',temp_basket)
#         validated_data['basket']=temp_basket
#         order_item,created=OrderItem.objects.get_or_create(**validated_data)
#         print('######## order_item first=',order_item)
#         # temp_order_item = OrderItem(basket=basket,user=user)
#         # serializer = self.get_serializer(temp_order_item,data=request.data)
#         if not created:
#             print('########not created')
#             order_item.quantity +=1
#             order_item.save()
#         return order_item
#         # return super(OrderItemSerializer,self).create(validated_data)

    

    
    # def create(self, validated_data):
    #     user = self.context.get('user')
    #     validated_data['user']=user
    #     return super(OrderItemSerializer,self).create(validated_data)
    # def save(self, **kwargs):
    #     print('validated-data in save*******basket,user********',self.validated_data)
    #     quantity=self.validated_data.pop('quantity')
    #     print('validated-data in save after pop(quantity)*******basket,user********',self.validated_data)
    #     data=OrderItem.objects.filter(self.validated_data)
    #     if data.exists():
    #         data[0].quantity=quantity
    #     else:
    #         OrderItem.objects.create(self.validated_data)
            


        # return super().save(**kwargs)



    
        # order_item,created=OrderItem.objects.get_or_create(**validated_data)
        # temp_order_item = OrderItem(basket=basket,user=user)
        # serializer = self.get_serializer(temp_order_item,data=request.data)
        # if not created:
            # print('########not created')
            # order_item.quantity += quantity
            # order_item.save()
        # return order_item
        # return super(ItemsSerializer,self).create(validated_data)



    # def create(self, validated_data):
    #     user = self.context.get('user')
    #     validated_data['user']=user
    #     return super(OrderItemSerializer,self).create(validated_data)
    # def create(self, validated_data):
    #     user = self.context.get('user')
    #     validated_data['user']=user
    #     # validated_data['quantity']=1
    #     try:
    #         print('######## try1')
    #         temp_basket = Basket.objects.get(user=user,payment=False)
    #     except Basket.DoesNotExist:
    #         raise ValidationError('you do not have temporary basket')
    #         # print('########except1')
    #         # # print('******receiver=',user.profile.values(receiver))
    #         # print('******receiver=',user.profile.receiver)
    #         # try:
    #         #     print('######## try2')
    #         #     receiver=user.profile.receiver
    #         # except :
    #         #     print('######## except2')
    #         #     raise NotFound('first complete your profile')
    #         # # if receiver is not None:
    #         # temp_basket = Basket.objects.create(user=user,receiver=receiver)
    #         # print('##temp_basket',temp_basket)
    #     validated_data['basket']=temp_basket
    #     try:
    #         print('######## try2')
    #         order_item=OrderItem.objects.get(**validated_data)
    #     except OrderItem.DoesNotExist:
    #         print('######## order_item does not exist')
    #         raise ValidationError('there is no such order_item ')
    #     if order_item.quantity > 1:
    #         print('######## quantity>1')
    #         order_item.quantity -= 1
    #         order_item.save()
    #         # return order_item
    #     elif order_item.quantity == 1:
    #         print('######## quantity==1')
    #         order_item.delete()
    #         # data={}
    #         # data['result']='order_item deleted from basket'
    #     else:
    #         print('######## quantity==0 or ?')
    #         order_item.delete()
    #         raise ValidationError('quantity not valid')
    #     return order_item

        # print('######## order_item first=',order_item)
        # # temp_order_item = OrderItem(basket=basket,user=user)
        # # serializer = self.get_serializer(temp_order_item,data=request.data)
        # if not created:
        #     print('########not created')
        #     order_item.quantity +=1
        #     order_item.save()
        # return order_item

class EditVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = ['id','price','discount','stock']