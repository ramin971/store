from django.contrib import admin,messages
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,\
    ProductImage,OrderItem,Basket,Profile,Address,ReceiverInformation,Province,Coupon
# from django.contrib.auth.models import User
from django.db.models.aggregates import Min,Sum,Avg

class DiscountFilter(admin.SimpleListFilter):
    title = 'discount'
    parameter_name = 'discount'

    def lookups(self, request, model_admin):
        return [
            ('<10','lt_10%'),
            ('<20&>10','between_10&20'),
            ('>20','gt_20%')
        ]
        
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(variations__discount__lt=10)
        elif self.value() == '<20&>10':
            return queryset.filter(variations__discount__range=[10,20])
        if self.value() == '>20':
            return queryset.filter(variations__discount__gt=20)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class VariationInline(admin.TabularInline):
    autocomplete_fields = ['color']
    model = Variation
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['category','info']
    list_select_related = ['category','category__parent']
    list_display = ['name','rate','category','sizes','colors','price','stocks','updated']
    prepopulated_fields = {'slug':('name',)}
    ordering = ['-updated']
    list_per_page = 10
    search_fields = ['name','category__istartswith']
    list_filter = ['category','updated',DiscountFilter]
    # list_filter = ['category','updated']
    inlines = [ProductImageInline,VariationInline]
    
    def price(self,obj):
        min_price = obj.variations.aggregate(price=Min('price'))
        return min_price['price']

    def stocks(self,obj):
        stocks = obj.variations.aggregate(stock=Sum('stock'))
        return stocks['stock']

    def sizes(self,obj):
        sizes=obj.variations.values_list('size__value',flat=True).distinct()
        return list(sizes)
        # return ','.join([str(i.value) for i in obj.size.all()])
        # return list(obj.size.all().values_list('value',flat=True))
    def colors(self,obj):
        colors = obj.variations.values_list('color__value',flat=True)
        return list(colors)

    def rate(self,obj):
        avg_rate = obj.rates.aggregate(avg=Avg('rate'))
        return avg_rate['avg']

    
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
    # filter_horizontal =['size']
    search_fields = ['color__value','product__name','size__value']
    list_editable = ['discount']
    actions = ['clear_discount','Ten_percent_discount']
    list_select_related = ['product','color','size']
    list_display = ['product','color','size','discount','price','stock','created','updated']
    
    @admin.action(description='Clear discount')
    def clear_discount(self,request,queryset):
        updated_discount = queryset.update(discount=None)
        self.message_user(request,f'{updated_discount}products were successfully updated',messages.ERROR)

    @admin.action(description='%%10 discount')
    def Ten_percent_discount(self,request,queryset):
        updated_discount = queryset.update(discount=10)
        self.message_user(request,f'{updated_discount}products were successfully updated',messages.SUCCESS)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user','variation','quantity','basket']
    # readonly_fields = ['user']

class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['variation']
    model = OrderItem
    extra = 1
    readonly_fields = ['user']
    

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['user','payment','get_total_price','status','receiver','tracking_code','ordered_date']
    ordering = ['payment','status','-ordered_date']
    search_fields = ['user','tracking_code__istartwith']
    readonly_fields = ['tracking_code','user','payment','get_total_price','coupon','ordered_date']
    list_filter = ['payment','status','ordered_date']
    radio_fields = {'status':admin.HORIZONTAL}
    list_editable = ['status']
    list_select_related = ['user','receiver','coupon']
    inlines = [OrderItemInline]
    list_per_page = 10


@admin.register(ReceiverInformation)
class ReceiverInformationAdmin(admin.ModelAdmin):
    list_display = ['full_name','national_code','address']
    list_select_related = ['address','address__province']
    readonly_fields = ['full_name','national_code','postal_code','phone','address']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['province','full_address']
    autocomplete_fields = ['province']

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','phone']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['product']
    # list_select_related = ['product','user']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product','image']
    list_select_related = ['product']

admin.site.register(Rating)
admin.site.register(Coupon)
