from django import forms
from .models import Sale, Purchase, Product, Supplier, Category, Brand
from datetime import date
from django.utils import timezone

class TransactionForm(forms.Form):
    TRANSACTION_TYPES = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
    ]
    
    # Transaction type choice
    transaction_type = forms.ChoiceField(choices=TRANSACTION_TYPES, required=True)
    
    # Common fields for both sales and purchases
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=True)
    quantity = forms.DecimalField(max_digits=20, decimal_places=2, required=True)
    # Use an HTML5 date input with a default value of today's date
    transaction_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        initial=timezone.now
    )
    
    # Sale-specific fields
    sale_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)  
    discount = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0)  
    
    # Purchase-specific fields
    purchase_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)  
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), required=False, empty_label="Select Supplier")
    
    def clean_transaction_date(self):
        today = date.today()

        # Get the current year and month
        current_year = today.year
        current_month = today.month
        transaction_date = self.cleaned_data.get('transaction_date')
        
         # Ensure transaction date is in the current month
        if transaction_date.year != current_year or transaction_date.month != current_month:
            raise forms.ValidationError('Transactions can only be added for the current month.')
        
        if transaction_date > date.today():
            raise forms.ValidationError("Transaction date cannot be in the future.")
        return transaction_date
    
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        
        # Validate sale-specific fields
        if transaction_type == 'sale':
            sale_price = cleaned_data.get('sale_price')
            if not sale_price:
                raise forms.ValidationError('Sale price is required for sales.')
        
        # Validate purchase-specific fields
        else:
            purchase_price = cleaned_data.get('purchase_price')
            if not purchase_price:
                raise forms.ValidationError('Purchase price is required for purchases.')

        return cleaned_data
    
class addProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'initial_stock', 'reorder_level', 'description', 'is_active']
    
    def clean_name(self):
        name = self.cleaned_data['name']
        # Get the product instance (if it's already in the database)
        product_id = self.instance.id
        
        # Check if any other product exists with the same name, excluding the current product
        if Product.objects.filter(name=name).exclude(id=product_id).exists():
            raise forms.ValidationError(f"A product with the name '{name}' already exists.")
        return name    
        
    def clean_initial_stock(self):
        initial_stock = self.cleaned_data.get('initial_stock')
        if initial_stock < 0:
            raise forms.ValidationError("Initial stock cannot be negative.")
        return initial_stock
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
        
class BrandsForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name', 'description']
        
#the excel form for uploading products        
class UploadExcelForm(forms.Form):
    file = forms.FileField()