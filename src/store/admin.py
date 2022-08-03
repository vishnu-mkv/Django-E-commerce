from django.contrib import admin

from store.models import Cart, CartEntry, Product

# Register your models here.

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartEntry)