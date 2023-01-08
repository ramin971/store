from django_filters.rest_framework import FilterSet,OrderingFilter,BooleanFilter
from .models import Product,Rating
# from django.db.models import Avg
class ProductFilter(FilterSet):
    stock = BooleanFilter(field_name='variations__stock',method='filter_stock')

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

        # labels do not need to retain order
        # field_labels={
            # 'username': 'User account',
        # }
    )

    class Meta:
        model = Product
        fields ={
            'category_id':['exact'],
            'variations__price':['gt','lt'],
            # 'stock':
            # 'price':['gt','lt'],

        }

# class CustomOrderingFilter(OrderingFilter):
#         def filter(self, qs, value):
#             if any(v == 'rate' for v in value):
#                 qs.order_by('avg_rate')
#             return super(CustomOrderingFilter, self).filter(qs, value)
