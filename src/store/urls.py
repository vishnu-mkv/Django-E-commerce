from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
        path('', views.ProductListView.as_view(),
         name='home'),
        path('products/create', views.ProductCreateView.as_view(),
         name='product-create'),
        path('products/<int:pk>/delete', views.ProductDeleteView.as_view(),
         name='product-delete'),
        path('products/<int:pk>/', views.ProductDetailView.as_view(),
         name='product-detail'),
        path('products/<int:pk>/update', views.ProductUpdateView.as_view(),
         name='product-update'),
        path('cart/', views.cart_detail,
        name='cart-detail'),
        path('cart/add', views.cart_add,
        name='cart-add'),
        path('cart/remove', views.cart_remove,
        name='cart-remove'),
]