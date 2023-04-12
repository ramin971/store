from django.shortcuts import render,get_object_or_404
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from .permissions import IsAdminOrReadOnly,IsAdminOrIsAuthenticated
from rest_framework.decorators import action,api_view,permission_classes

from rest_framework.decorators import api_view

from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveUpdateAPIView,ListCreateAPIView,\
    RetrieveUpdateDestroyAPIView,CreateAPIView
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,\
    ProductImage,OrderItem,Basket,Profile,Address,ReceiverInformation,Province,Coupon
from .serializers import BasketSerializer,ProfileSerializer,CouponSerializer,\
    ReceiverInformationSerializer,ProductSerializer,CategorySerializer,AddImageSerializer,\
        RatingSerializer,CommentSerializer,ProductDetailSerializer,AddOrderItemSerializer,\
            EditRemoveOrderItemSerializer,VariationSerializer,EditVariationSerializer
# from django.db.models.aggregates import Sum,Avg,Count,Min,Max
from django.db.models import Avg,Sum,Min,Max,Count
# Create your views here.
    


class ProductList(ListCreateAPIView):
    queryset = Product.objects.annotate(avg_rate=Avg('rates__rate')
    ,stock=Sum('variations__stock'),price=Min('variations__price')).order_by('-updated')

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    # filterset_fields=['']
    filterset_class = ProductFilter
    pagination_class = PageNumberPagination
    
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAdminUser()] 
    
    def get_serializer_context(self):
        return {'request':self.request}

    # overrid Response of create method because created obj has not annotate methods that define in queryset(up)
    def create(self, request, *args, **kwargs):
        # super(ProductList,self).create(request, *args, **kwargs)
        # instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        result = {
            "message": "success created",
            }
        return Response(result,status=status.HTTP_201_CREATED)


class AddImage(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = AddImageSerializer
    permission_classes = [IsAdminUser]
    # overrid Response of create method because created obj has not annotate methods that define in queryset(up)
    def create(self, request, *args, **kwargs):
        # super(ProductList,self).create(request, *args, **kwargs)
        # instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        result = {
            "message": "Images added successfully",
            }
        return Response(result,status=status.HTTP_201_CREATED)



class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.annotate(avg_rate=Avg('rates__rate')).prefetch_related('info',
    'images','comments','comments__user','variations','variations__size','variations__color')
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    # pagination_class = PageNumberPagination
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = DetailFilter
    # filterset_fields=['variations__color','variations__size']
    
    def get_serializer_context(self):
        return {'request':self.request}
    
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAdminUser()]

    # add paginated comments to product-detail
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer=self.get_serializer(instance)

        paginator = PageNumberPagination()
        paginator.page_size = 2
        result_page=paginator.paginate_queryset(instance.comments.all(), request)
        comment_serializer=CommentSerializer(result_page,many=True)

        data={}
        data['product']= serializer.data
        data['comments']=comment_serializer.data
        return paginator.get_paginated_response(data)

    # add partial=True to PUT method
    def put(self, request, *args, **kwargs):
        kwargs['partial'] = True 
        return self.update(request, *args, **kwargs)


class CategoryList(ListCreateAPIView):
    queryset = Category.objects.select_related('parent').annotate(products_count=Count('products'))
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAdminUser()]

class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.select_related('parent').annotate(products_count=Count('products'))
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    # http_method_names = ['get','patch','delete']
    
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAdminUser()]

    # add partial=True to PUT method
    def put(self, request, *args, **kwargs):
        kwargs['partial'] = True 
        return self.update(request, *args, **kwargs)

    # ????????
    # def update(self, request, *args, **kwargs):
    #     kwargs['partial']=True
    #     partial=kwargs['partial']
    #     if 'parent' in request.data:
    #         print('1')
    #         parent_name=request.data.get('parent')
    #         # print('**********parentv=',parent_name,type(parent_name))
    #         if parent_name:
    #             print('2')
    #             parent_obj=get_object_or_404(Category,name=parent_name)
    #             print('parent',parent_obj,type(parent_obj))
    #             instance=Category(parent=parent_obj)
    #             # serializer.save(parent=parent_obj)
    #             serializer = self.get_serializer(instance, data=request.data, partial=partial)

    #             # serializer.save(temp_category,data=request.data)
    #         else:
    #             print('3')
    #             instance=Category(parent=None)
    #             # serializer.save(parent=None)
    #             serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #             # serializer.save(temp_category,data=request.data)
    #         print('4')
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #     print('##################')
    #     # instance = self.get_object()
    #     # serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     # return self.update(request, *args, **kwargs)
    #     return super().update(request, *args, **kwargs)

    #     # return super().update()
    # # def update(self, request, *args, **kwargs):
    #     # return super().update(request, *args, **kwargs)

# add this feuture to product_detail 
class Ratings(CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    def get_serializer_context(self):
        return {'user':self.request.user}

class Comments(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    def get_serializer_context(self):
        return {'user':self.request.user}


@api_view(['GET'])
def province_choices(request):
    # print('######',Province.objects.first())
    queryset = Province.PROVINCE_CHOICES
    q = request.query_params.get('q')
    province_list=[province[0] for province in queryset]
    if q:
        province_list = [province for province in province_list if q in province]
    data = {}
    data['provinces'] = province_list

    # if q:
    #     provinces=[]
    #     for province in province_list:
    #         if q in province:
    #             provinces.append(province)
    #     data['provinces'] = provinces

    return Response(data,status=status.HTTP_200_OK)



class ReceiverInformations(CreateAPIView):
    queryset = ReceiverInformation.objects.all()
    serializer_class = ReceiverInformationSerializer

class ReceiverInformationDetail(RetrieveUpdateDestroyAPIView):
    queryset = ReceiverInformation.objects.all()
    serializer_class = ReceiverInformationSerializer
    permission_classes = [IsAuthenticated]

    # add partial=True to PUT method
    def put(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(ReceiverInformationDetail,self).put(request, *args, **kwargs)

class Coupons(ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

class CouponDetail(RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

    # add partial=True to PUT method
    def put(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(CouponDetail,self).put(request, *args, **kwargs)
    
@api_view(['GET','PUT'])
@permission_classes((IsAuthenticated,))
def profile_me(request):
    user = request.user
    print('###',user)
    profile = get_object_or_404(Profile,user=user.id)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data,status=status.HTTP_200_OK)
    # elif request.method == 'POST':
    #     serializer = ProfileSerializer(user=user,data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data,status=status.HTTP_201_CREATED)
    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)


class Profiles(ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminOrIsAuthenticated] 

    def get_serializer_context(self):
        return {'user':self.request.user}
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [IsAdminUser()]
    #     return [IsAuthenticated()]

    # @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated]) # methods not work . because we use ListCreateAPIView must use viewset
    # def me(self,request):
    #     print('#####',request.user)
    #     profile = get_object_or_404(Profile,user=request.user)
    #     if request.method=='GET':
    #         serializer = ProfileSerializer(profile)
    #         return Response(serializer.data,status=status.HTTP_200_OK)
    #     elif request.method=='PUT':
    #         serializer = ProfileSerializer(profile,data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)

    # def get_queryset(self):
    #     # if self.kwargs.get('pk',False):
    #     #     print('##########pk1=',self.kwargs)
    #     #     return Profile.objects.all()
    #     # else:
    #     #     print('##########pk2me=',self.kwargs)
    #     #     print('##########user=',self.request.user)
    #     #     return Profile.objects.get(user=self.request.user)



class ProfileDetail(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]
   
    def put(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(ProfileDetail,self).put(request, *args, **kwargs)


class Baskets(ListCreateAPIView):
    # queryset = Basket.objects.all().prefetch_related('order_items','order_items__variation').select_related('coupon','receiver')
    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Basket.objects.filter(user=self.request.user)\
            .prefetch_related('order_items','order_items__variation','order_items__variation__product'\
                          ,'order_items__variation__color','order_items__variation__size')\
                            .select_related('coupon','receiver')

    def get_serializer_context(self):
        return {'user':self.request.user}

    
class BasketDetail(RetrieveUpdateDestroyAPIView):
    queryset = Basket.objects.all()\
        .prefetch_related('order_items','order_items__variation','order_items__variation__product'\
                          ,'order_items__variation__color','order_items__variation__size')\
            .select_related('coupon','receiver')

    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticated]
    # was_paid = True
    was_paid = False


    def get_serializer_context(self):
        return {'was_paid':self.was_paid}

    def put(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(BasketDetail,self).put(request, *args, **kwargs)

class AddItems(CreateAPIView):
    queryset = OrderItem.objects.select_related('variation','variation__product','variation__color','variation__size','variation__product__category')
    serializer_class = AddOrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'user':self.request.user}

class EditRemoveItems(RetrieveUpdateDestroyAPIView):
    http_method_names = ['get','patch','delete']
    queryset = OrderItem.objects.all()
    serializer_class = EditRemoveOrderItemSerializer
    permission_classes = [IsAuthenticated]


    # def create(self, request, *args, **kwargs):
    #     # instance = self.get_object()
    #     user = request.user
    #     try:
    #         basket = Basket.objects.get(user=user,payment=False)
    #     except Basket.DoesNotExist:
    #         # print('******receiver=',user.profile.values(receiver))
    #         print('******receiver=',user.profile.receiver)
    #         try:
    #             receiver=user.profile.receiver
    #         except :
    #             raise NotFound('first complete your profile')
    #         # if receiver is not None:
    #         basket = Basket.objects.create(user=user,receiver=receiver)

        
    #     temp_order_item = OrderItem(basket=basket,user=user)
    #     serializer = self.get_serializer(temp_order_item,data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # return super(AddToCart,self).create(request, *args, **kwargs)


# api_view(['POST'])
# def add_to_basket(request):
#     # step basket
#     user = request.user
#     try:
#         basket = Basket.objects.get(user=user,payment=False)
#     except Basket.DoesNotExist:
#         print('******receiver=',user.profile.values(receiver))

#         print('******receiver=',user.profile.receiver)
#         try:
#             receiver=user.profile.receiver
#         except :
#             raise NotFound('first complete your profile')
#         # if receiver is not None:
#         basket = Basket.objects.create(user=user,receiver=receiver)
    
class EditVariation(RetrieveUpdateDestroyAPIView):
    queryset = Variation.objects.all()
    # serializer_class = VariationSerializer
    serializer_class = EditVariationSerializer
    permission_classes = [IsAdminUser]

