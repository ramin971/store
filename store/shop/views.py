from django.shortcuts import render,get_object_or_404
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView,CreateAPIView
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,\
    ProductImage,OrderItem,Basket,Profile,Address,ReceiverInformation,Province
from .serializers import ProductSerializer,CategorySerializer,RatingSerializer
# from django.db.models.aggregates import Sum,Avg,Count,Min,Max
from django.db.models import Avg,Sum,Min,Max,Count
# Create your views here.
    


class ProductList(ListCreateAPIView):
    queryset = Product.objects.annotate(avg_rate=Avg('rates__rate')
        ,stock=Sum('variations__stock'),price=Min('variations__price')).order_by('-updated')

    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_fields=['']
    filterset_class = ProductFilter

   
    def get_serializer_context(self):
        return {'request':self.request}

    # def create(self, request, *args, **kwargs):
    #     request.data._mutable = True
    #     variations=request.data.pop('variations')
    #     json_variations=json.loads(variations)
    #     request.data['variations']=json_variations
    #     # request.data=JSONRenderer().render(request.data)
    #     super().create(request, *args, **kwargs)

class ProductByCategory(ListAPIView):
    serializer_class=ProductSerializer
    # lookup_field='slug'
    def get_queryset(self):
        # print(f'kwargs={self.kwargs},args={self.args}')
        return Product.objects.filter(category__slug__iexact=self.kwargs['slug']).annotate(avg_rate=Avg('rates__rate')
        ,stock=Sum('variations__stock'),price=Min('variations__price'))
    def get_serializer_context(self):
        return {'request':self.request}

class CategoryList(ListCreateAPIView):
    queryset = Category.objects.select_related('parent').all().annotate(products_count=Count('products'))
    serializer_class = CategorySerializer

class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.select_related('parent').all()
    serializer_class = CategorySerializer

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
class Rating(CreateAPIView):
    queryset=Rating.objects.all()
    serializer_class = RatingSerializer
    def get_serializer_context(self):
        return {'user':self.request.user}