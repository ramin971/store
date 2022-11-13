from django.contrib import admin
from .models import Product,Category,Color,Size,Rating,Comment,Info,Variation,ProductImage




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','category','discount','created','updated']
    prepopulated_fields = {'slug':('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    # list_display = ['name','parents']

    prepopulated_fields = {'slug':('name',)}


# @admin.register(Color)
# class ColorAdmin(admin.ModelAdmin):
#     list_display = ['value']

# @admin.register(Size)
# class SizeAdmin(admin.ModelAdmin):
#     list_display = ['value']

# @admin.register(Color)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['value']


# @admin.register(Variation)
# class VariationAdmin(admin.ModelAdmin):
#     list_display = ['product','color','discount','price','stock','created']

admin.site.register(Rating)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Info)
admin.site.register(Comment)
# admin.site.register(Category)