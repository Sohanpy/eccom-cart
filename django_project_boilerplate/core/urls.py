from django.urls import path

from .views import HomePageView  , ProductDetailView ,  Cart , add_to_cart , remove_from_cart , remove_single_item_from_cart , CheckoutView

app_name = 'core'

urlpatterns = [
    path('', HomePageView.as_view() , name = 'home'),
    path('cart', Cart.as_view() , name = 'cart'),
    path('checkout/', CheckoutView.as_view() , name = 'Checkout'),
    path('detail/<slug>/', ProductDetailView.as_view() , name = 'detail'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-single-item-from-cart/<slug>/', add_to_cart, name='remove-single-item-from-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart , name='remove_single_item_from_cart'),

]