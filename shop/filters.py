from django_filters.rest_framework import RangeFilter,CharFilter,FilterSet,OrderingFilter,BooleanFilter,NumericRangeFilter
from .models import Product,Rating,Variation,Size
from django.db.models import Q
from django.db.models import Avg,Max


class ProductFilter(FilterSet):
    q = CharFilter(label='search',method='custom_search')
    stock = BooleanFilter(field_name='variations__stock',method='filter_stock')
    size = CharFilter(label='size',method='custom_size')
    # size = ModelMultipleChoiceFilter(field_name='variations__size',to_field_name='value',queryset=Size.objects.all()) #best but not working
    # price = NumericRangeFilter(label='price_range',field_name='variations__price')
    price = RangeFilter(method='custom_price',label='price_range')


    def custom_price(self,queryset,name,value):
        print('#price-value',value,'#price-name',name) #-->price-value slice(Decimal('2000000'), Decimal('5000000'), None) #price-name price
        # print('$$$$$value-split',value.split())
        qp=self.request.query_params
        price_min=qp.get('price_min',0)
        max_price=queryset.aggregate(max_price=Max('variations__price'))['max_price']
        print('$$$$$maxprice:',max_price,type(max_price))
        price_max=qp.get('price_max',max_price)
        queryset = queryset.filter(variations__price__range=(price_min,price_max))

        return queryset
        
   

    def custom_size(self,queryset,name,value):
        print('#size-value',value,'#size-name',name)
        print('#qp',self.request.query_params)
        qp=self.request.query_params.getlist('size')
        print(qp)
        queryset = queryset.filter(variations__size__value__in=qp)
        return queryset

    def custom_search(self,queryset,name,value):
        queryset = queryset.filter(Q(name__icontains=value) | Q(info__value__icontains=value))
        return queryset

    def filter_stock(self,queryset,name,value):
        print('#value',value,'#name',name)
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

            
    


    o = OrderingFilter(
        # tuple-mapping retains order
        fields=(
            # ('updated', 'new'),
            ('variations__price', 'price'),
            ('avg_rate', 'rate'),
            # ('stock','stock')
        ),

        # oprional
        choices=[
            ('price', 'Price'),
            ('-price', 'Price(descending)'),
            ('-rate', 'rate(descending)')
        ]

        # labels do not need to retain order
        # field_labels={
            # 'username': 'User account',
        # }
    )

    class Meta:
        model = Product
        # fields=['size']
        fields ={
            'category_id':['exact'],
            'variations__price':['gt','lt'], #optional(duplicated)
            'variations__size':['exact'], #in url use id of size.#optional(duplicated)

        }

# class DetailFilter(FilterSet):
#     class Meta:
#         model = Product
#         fields ={
#             'variations__color':['exact'],
#             'variations__size':['exact']
#         }