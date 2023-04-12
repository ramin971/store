from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns=[
    path('products/',views.ProductList.as_view()),
    path('products/<int:pk>/',views.ProductDetail.as_view()),
    path('variation/<int:pk>/',views.EditVariation.as_view()),
    path('image/',views.AddImage.as_view()),
    path('rate/',views.Ratings.as_view()),
    path('comment/',views.Comments.as_view()),
    path('category/',views.CategoryList.as_view()),
    path('category/<int:pk>/',views.CategoryDetail.as_view()),
    path('receiver/',views.ReceiverInformations.as_view()),
    path('receiver/<int:pk>/',views.ReceiverInformationDetail.as_view()),
    path('province/',views.province_choices),
    path('coupon/',views.Coupons.as_view()),
    path('coupon/<int:pk>/',views.CouponDetail.as_view()),
    path('profile/',views.Profiles.as_view()),
    # path('profile/me/',views.ProfilesMe.as_view()), need viewset action
    path('profile/me/',views.profile_me),
    path('profile/<int:pk>/',views.ProfileDetail.as_view()),
    path('basket/',views.Baskets.as_view()),# don't need maybe
    path('basket/<uuid:pk>/',views.BasketDetail.as_view()),
    path('items/',views.AddItems.as_view()),
    path('items/<int:pk>',views.EditRemoveItems.as_view()),
    





]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

