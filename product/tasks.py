from celery import shared_task
from django.utils import timezone
from django.db.models import Sum
from .models import Product, MonthlyData, Purchase, Sale

@shared_task
def save_monthly_data():
    # Get the current date (1st of the current month)
    now = timezone.now()
     # Check if it's the first day of the month
    if now.day != 1:
        return  # If it's not the first day, do nothing

    current_year = now.year
    current_month = now.month

    # Calculate the previous month and year (i.e., the month we want to save data for)
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    # Calculate the month **before** the previous month (for the starting stock)
    if previous_month == 1:
        month_before_last = 12
        year_before_last = previous_year - 1
    else:
        month_before_last = previous_month - 1
        year_before_last = previous_year

    # Loop through all products to calculate and save monthly data for the previous month
    for product in Product.objects.all():
        # Get the starting stock from the **ending stock of two months ago** (August for September data)
        try:
            # Fetch data for the month before the previous month (e.g., August when saving for September)
            last_month_data = MonthlyData.objects.get(
                product=product,
                year=year_before_last,
                month=month_before_last
            )
            starting_stock = last_month_data.ending_stock
        except MonthlyData.DoesNotExist:
            # If no data for August exists, use the initial stock
            starting_stock = product.initial_stock

        # Calculate total purchases and sales for the **previous month** (e.g., September 2024)
        total_purchases = Purchase.objects.filter(
            product=product,
            purchase_date__year=previous_year,
            purchase_date__month=previous_month
        ).aggregate(total_quantity=Sum('purchase_quantity'), total_cost=Sum('purchase_price'))

        total_sales = Sale.objects.filter(
            product=product,
            sale_date__year=previous_year,
            sale_date__month=previous_month
        ).aggregate(total_quantity=Sum('sale_quantity'), total_revenue=Sum('sale_price'))

        # Set default values if no purchases or sales were made
        total_purchases_quantity = total_purchases['total_quantity'] or 0
        total_purchases_cost = total_purchases['total_cost'] or 0
        total_sales_quantity = total_sales['total_quantity'] or 0
        total_sales_revenue = total_sales['total_revenue'] or 0

        # Calculate ending stock for the previous month
        ending_stock = starting_stock + total_purchases_quantity - total_sales_quantity

        # Save the data for the **previous month** (e.g., saving data for September on October 1st)
        MonthlyData.objects.update_or_create(
            product=product,
            year=previous_year,
            month=previous_month,
            defaults={
                'starting_stock': starting_stock,
                'total_purchases': total_purchases_quantity,
                'total_sales': total_sales_quantity,
                'ending_stock': ending_stock,
                'total_purchase_cost': total_purchases_cost,
                'total_sales_revenue': total_sales_revenue
            }
        )
