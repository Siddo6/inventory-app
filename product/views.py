from django.shortcuts import render, redirect, get_object_or_404
from .forms import TransactionForm, addProductForm, CategoryForm, BrandsForm, UploadExcelForm
from .models import Sale, Purchase, Product, Category, Brand, MonthlyData
import pandas as pd
from django_pandas.io import read_frame 
from django.utils import timezone
from django.db.models import Sum, F

def upload_products(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        existing_products = []
        new_products = []

        if form.is_valid():
            excel_file = request.FILES['file']

            try:
                df = pd.read_excel(excel_file)

                # Convert 'Initial stock' to numeric and replace NaN with 0 globally
                df['Initial stock'] = pd.to_numeric(df['Initial stock'], errors='coerce').fillna(0)

                for index, row in df.iterrows():
                    product_name = row['Product Name']
                    category_name = str(row.get('Category', '')).strip() if not pd.isna(row.get('Category')) else None
                    brand_name = str(row.get('Brand', '')).strip() if not pd.isna(row.get('Brand')) else None
                    initial_stock = row['Initial stock']

                    # Check if the category exists, if not, leave it as None
                    category = Category.objects.get_or_create(category_name=category_name)[0] if category_name else None

                    # Check if the brand exists, if not, leave it as None
                    brand = Brand.objects.get_or_create(brand_name=brand_name)[0] if brand_name else None

                    # Check if the product already exists
                    existing_product = Product.objects.filter(name=product_name, category=category, brand=brand).first()

                    if existing_product:
                        # Add to the existing products list to show an error
                        existing_products.append({
                            'name': product_name,
                            'category': category_name,
                            'brand': brand_name,
                            'edit_url': f"/edit_product/{existing_product.id}/"  # Example edit URL
                        })
                    else:
                        # Create the new product
                        Product.objects.create(
                            name=product_name,
                            category=category,
                            brand=brand,
                            initial_stock=initial_stock,
                            current_stock=initial_stock
                        )
                        new_products.append(product_name)

                # If there are any existing products, show the error with an option to edit
                if existing_products:
                    return render(request, 'upload_products.html', {
                        'form': form,
                        'existing_products': existing_products,
                        'new_products': new_products
                    })

                # If all products are new, redirect to success
                return redirect('dashboard')

            except Exception as e:
                # Handle exceptions (e.g., invalid file format, missing columns)
                return render(request, 'upload_products.html', {'form': form, 'error': str(e)})
    else:
        form = UploadExcelForm()

    return render(request, 'upload_products.html', {'form': form})

def add_product(request):
    if request.method == 'POST':
        form = addProductForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the new product to the database
            return redirect('/')  # Redirect
    else:
        form = addProductForm()

    return render(request, 'add_product.html', {'form': form})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = addProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = addProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})

def add_category(request):
    category_form = CategoryForm()  # Instantiate a blank form
    brand_form = BrandsForm()
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()  # Saves the new product to the database
            return redirect('dashboard')  # Redirect
        else:
            # Re-render the form with errors
            return render(request, 'add_category_and_brand.html', {
        'category_form': category_form,
        'brand_form': brand_form,
    })
    else:
        category_form = CategoryForm()

    return render(request, 'add_category_and_brand.html', {
        'category_form': category_form,
        'brand_form': brand_form,
    })

def add_brand(request):
    category_form = CategoryForm()  # Instantiate a blank form
    brand_form = BrandsForm()
    if request.method == 'POST':
        brand_form = BrandsForm(request.POST)
        if brand_form.is_valid():
            brand_form.save()  # Saves the new product to the database
            return redirect('dashboard')  # Redirect
        else:
            # Re-render the form with errors
            return render(request, 'add_category_and_brand.html', {
        'category_form': category_form,
        'brand_form': brand_form,
    })
    else:
        brand_form = BrandsForm()

    return render(request, 'add_category_and_brand.html', {
        'category_form': category_form,
        'brand_form': brand_form,
    })

def add_category_and_brand(request):
    category_form = CategoryForm()  # Instantiate a blank form
    brand_form = BrandsForm()  # Instantiate a blank form

    return render(request, 'add_category_and_brand.html', {
        'category_form': category_form,
        'brand_form': brand_form,
    })

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction_type = form.cleaned_data['transaction_type']
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            transaction_date = form.cleaned_data['transaction_date']

            if transaction_type == 'sale':
                # Create a sale record
                sale_price = form.cleaned_data['sale_price']
                discount = form.cleaned_data['discount'] or 0
                
                # Update the product's stock for a sale
                if quantity <= product.current_stock:
                    product.current_stock -= quantity
                    product.save()  # Save the updated stock
                
                    Sale.objects.create(
                        product=product,
                        sale_quantity=quantity,
                        sale_price=sale_price,
                        discount=discount,
                        sale_date=transaction_date
                    )
                    return redirect('dashboard')
                else:
                    # Handle the case where the sale quantity exceeds current stock
                    form.add_error('quantity', f"Not enough stock for {product.name}. Current stock is {product.current_stock}.")
            elif transaction_type == 'purchase':
                # Create a purchase record
                purchase_price = form.cleaned_data['purchase_price']
                supplier = form.cleaned_data['supplier']
                
                # Update product's stock
                product.current_stock += quantity
                product.save()  # Save the updated stock
                
                Purchase.objects.create(
                    product=product,
                    purchase_quantity=quantity,
                    purchase_price=purchase_price,
                    purchase_date=transaction_date,
                    supplier=supplier
                )
                return redirect('dashboard')  # Redirect to a success page after saving
    else:
        form = TransactionForm()

    return render(request, 'add_transaction.html', {'form': form})

def current_month_summary(request):
    now = timezone.now()
    current_year = now.year
    current_month = now.month
   
    if now.month == 1:
            year = now.year - 1
            month = 12
    else:
            year = now.year
            month = now.month - 1
    
    # Query total purchases for the current month
    purchases = Purchase.objects.filter(
        purchase_date__year=current_year,
        purchase_date__month=current_month
    ).values('product__name').annotate(
        total_purchases=Sum('purchase_quantity'),
        total_cost=Sum(F('purchase_quantity') * F('purchase_price'))
    )
    
    # Query total sales for the current month
    sales = Sale.objects.filter(
        sale_date__year=current_year,
        sale_date__month=current_month
    ).values('product__name').annotate(
        total_sales=Sum('sale_quantity'),
        total_revenue=Sum(F('sale_quantity') * (F('sale_price') - F('discount')))
    )
    
    # Get current stock for each product
    products = Product.objects.all().values('name', 'current_stock')

    # Query the starting stock from MonthlyData or use the initial stock from the Product model
    starting_stocks = MonthlyData.objects.filter(
        year=year,
        month=month
    ).values('product__name', 'ending_stock')

    # Convert starting stocks to a dictionary for easier lookup
    starting_stock_dict = {s['product__name']: s['ending_stock'] for s in starting_stocks}

    # Merge purchases and sales into a summary dictionary
    summary = {}
    
    # Add purchases to the summary
    for p in purchases:
        summary[p['product__name']] = {
            'total_purchases': p['total_purchases'],
            'total_cost': p['total_cost'],
            'total_sales': 0,  # Default for sales
            'total_revenue': 0,  # Default for revenue
            'current_stock': 0,  # Default for stock
            'starting_stock': starting_stock_dict.get(p['product__name'], 0)  # Get from MonthlyData or default to 0
        }

    # Add sales to the summary (and update if the product already exists)
    for s in sales:
        if s['product__name'] in summary:
            summary[s['product__name']].update({
                'total_sales': s['total_sales'],
                'total_revenue': s['total_revenue']
            })
        else:
            summary[s['product__name']] = {
                'total_purchases': 0,  # Default for purchases
                'total_cost': 0,  # Default for cost
                'total_sales': s['total_sales'],
                'total_revenue': s['total_revenue'],
                'current_stock': 0,  # Default for stock
                'starting_stock': starting_stock_dict.get(s['product__name'], 0)  # Get from MonthlyData or default to 0
            }
    
    # Add current stock to the summary
    for product in products:
        if product['name'] in summary:
            summary[product['name']]['current_stock'] = product['current_stock']
        else:
            summary[product['name']] = {
                'total_purchases': 0,
                'total_cost': 0,
                'total_sales': 0,
                'total_revenue': 0,
                'current_stock': product['current_stock'],
                'starting_stock': starting_stock_dict.get(product['name'], 0)  # Get from MonthlyData or default to 0
            }
    
    # Convert summary to a list for rendering in the template
    summary_data = [{'product_name': key, **value} for key, value in summary.items()]

    # Render the summary to the template
    return render(request, 'current_month_summary.html', {
        'summary_data': summary_data,
        'current_month': current_month,
        'current_year': current_year,
    })


def past_month_data(request, year=None, month=None):
    now = timezone.now()
    
    # If no year or month is provided, default to the previous month
    if year is None or month is None:
        if now.month == 1:
            year = now.year - 1
            month = 12
        else:
            year = now.year
            month = now.month - 1

    # Query the MonthlyData for the selected month and year
    monthly_data = MonthlyData.objects.filter(year=year, month=month)

    # Convert the queryset into a list of dictionaries for rendering in the template
    summary_data = list(monthly_data.values(
        'product__name', 
        'starting_stock', 
        'total_purchases', 
        'total_sales', 
        'ending_stock', 
        'total_purchase_cost', 
        'total_sales_revenue'
    ))

    # Render the summary to the template
    return render(request, 'past_month_data.html', {
        'summary_data': summary_data,
        'selected_month': month,
        'selected_year': year,
    })
    
    
