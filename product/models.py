from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

current_year = datetime.now().year
current_month = datetime.now().month

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,blank=True, null=True, db_index=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField( db_index=True, default=timezone.now)
    current_stock = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    initial_stock = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    reorder_level = models.DecimalField(max_digits=20, decimal_places=2, default=10)
    
    def save(self, *args, **kwargs):
        # If this is a new product (i.e., first time saving)
        if self._state.adding and not self.current_stock:
            self.current_stock = self.initial_stock
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Purchase(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_index=True)
    purchase_date = models.DateField(db_index=True)
    purchase_quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    
    @property
    def total_cost(self):
        return self.purchase_quantity * self.purchase_price
    
    def __str__(self):
        return f"{self.product} - {self.purchase_quantity} units @ {self.purchase_price} each"


class Sale(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_index=True)
    sale_date = models.DateField(db_index=True)
    sale_quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    @property
    def total_revenue(self):
        return (self.sale_quantity * self.sale_price) - self.discount
    
    def __str__(self):
        return f"{self.product} - {self.sale_quantity} units @ {self.sale_price} each"


class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True) 
    
    def __str__(self):
        return self.category_name

class Brand(models.Model):
    brand_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.brand_name


class MonthlyData(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    starting_stock = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # Stock level at the start of the month
    total_purchases = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_sales = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    ending_stock = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_purchase_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_sales_revenue = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        unique_together = ['product', 'year', 'month']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['year', 'month']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.year}-{self.month}"

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.supplier_name