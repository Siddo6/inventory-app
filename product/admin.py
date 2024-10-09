from django.contrib import admin
from .models import Product, Purchase, Sale

# Register the models
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Sale)