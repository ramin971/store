from django_filters.rest_framework import FilterSet,OrderingFilter
from .models import Product,Rating
# from django.db.models import Avg
class ProductFilter(FilterSet):
    # rate = ModelChoiceFilter(queryset=Rating.objects.all())
    


    o = OrderingFilter(
        # tuple-mapping retains order
        fields=(
            # ('updated', 'new'),
            ('variations__price', 'price'),
            ('avg_rate', 'rate'),
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
            'variations__price':['gt','lt']
        }

class CustomOrderingFilter(OrderingFilter):
        def filter(self, qs, value):
            if any(v == 'rate' for v in value):
                qs.order_by('avg_rate')
            return super(CustomOrderingFilter, self).filter(qs, value)
