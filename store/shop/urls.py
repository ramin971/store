from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns=[
    path('products/',views.ProductList.as_view(),name='product_list'),
    # path('products/<int:pk>/',views.ProductDetail.as_view(),name='product_detail'),
    # path('products/<str:slug>/',views.ProductByCategory.as_view(),name='product_by_category'),
    path('rate/',views.Rating.as_view()),
    path('category/',views.CategoryList.as_view(),name='category_list'),
    path('category/<int:pk>/',views.CategoryDetail.as_view(),name='category_detail')
]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

