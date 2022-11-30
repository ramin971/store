from django.contrib import admin,messages
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,ProductImage
from django.db.models import Avg

class DiscountFilter(admin.SimpleListFilter):
    title = 'discount'
    parameter_name = 'discount'

    def lookups(self, request, model_admin):
        return [
            ('<10','low'),
            ('<20&>10','mid'),
            ('>20','big')
        ]
        
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(discount__lt=10)
        elif self.value() == '<20&>10':
            return queryset.filter(discount__range=[10,20])
        if self.value() == '>20':
            return queryset.filter(discount__gt=20)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class VariationInline(admin.TabularInline):
    autocomplete_fields = ['color']
    model = Variation
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category','size','info']
    actions = ['clear_discount','Ten_percent_discount']
    list_display = ['name','rate','category','discount','sizes','created','updated']
    prepopulated_fields = {'slug':('name',)}
    list_editable = ['discount']
    list_select_related = ['category','category__parent']
    ordering = ['-updated']
    list_per_page = 10
    search_fields = ['name','category__istartswith']
    list_filter = ['category','updated',DiscountFilter]
    inlines = [ProductImageInline,VariationInline]
    

    def sizes(self,obj):
        # return ','.join([str(i.value) for i in obj.size.all()])
        return list(obj.size.all().values_list('value',flat=True))

    def rate(self,obj):
        avg_rate = obj.rates.aggregate(avg=Avg('rate'))
        return avg_rate['avg']

    @admin.action(description='Clear discount')
    def clear_discount(self,request,queryset):
        updated_discount = queryset.update(discount=None)
        self.message_user(request,f'{updated_discount}products were successfully updated',messages.ERROR)

    @admin.action(description='%%10 discount')
    def Ten_percent_discount(self,request,queryset):
        updated_discount = queryset.update(discount=10)
        self.message_user(request,f'{updated_discount}products were successfully updated',messages.SUCCESS)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    # list_select_related = ['parent']
    # list_display = ['name','parents']

    prepopulated_fields = {'slug':('name',)}


@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    list_display = ['value']
    search_fields = ['value']

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['value']
    search_fields = ['value']

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['value']
    search_fields = ['value']


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    search_fields = ['color']
    list_display = ['product','colors','discount','price','stock','created']
    # list_display = ['product','discount','price','stock','created']

    # list_select_related = ['product']
    def colors(self,obj):
        # return [obj.color.all().values_list('value',flat=True)]
        return list(obj.color.all().values_list('value',flat=True))


admin.site.register(Rating)
# admin.site.register(Color)
admin.site.register(ProductImage)
# admin.site.register(Info)
admin.site.register(Comment)
# admin.site.register(Variation)