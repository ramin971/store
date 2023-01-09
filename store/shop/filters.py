from django_filters.rest_framework import CharFilter,MultipleChoiceFilter,ModelChoiceFilter,ModelMultipleChoiceFilter,FilterSet,OrderingFilter,BooleanFilter,ChoiceFilter
from .models import Product,Rating,Variation,Size
from django.db.models import Q
# from django.db.models import Avg

# SIZE_CHOICES=[(str(i),str(i)) for i in range(40,47)]
# SIZE_CHOICES=Size.options.value.choieces

class ProductFilter(FilterSet):
    q = CharFilter(label='search',method='custom_search')
    stock = BooleanFilter(field_name='variations__stock',method='filter_stock')
    # size = MultipleChoiceFilter(choices=Size.VALUE_CHOICES)
    # size = ModelMultipleChoiceFilter(field_name='variations__size',to_field_name='value',queryset=Size.objects.all()) #best but not working
    # size = ModelMultipleChoiceFilter(field_name='variations__size',to_field_name='size',queryset=Variation.objects.all().values_list('size__value',flat=True).distinct())
    # size = ModelChoiceFilter(queryset=variation)
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
            'variations__price':['gt','lt'],
            'variations__size':['exact'], #in url use id of size

            # 'variations__size__VALUE_CHOICES':['exact']

            # 'variations__size__value':['exact'] taki

            # 'price':['gt','lt'],

        }

# class CustomOrderingFilter(OrderingFilter):
#         def filter(self, qs, value):
#             if any(v == 'rate' for v in value):
#                 qs.order_by('avg_rate')
#             return super(CustomOrderingFilter, self).filter(qs, value)
