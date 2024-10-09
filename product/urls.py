from django.urls import path
from . import views

urlpatterns = [
    path('add_transaction', views.add_transaction, name='add_transaction'),
    path('add_product', views.add_product, name='add_product'),
    path('add_category', views.add_category, name='add_category'),
    path('add_brand', views.add_brand, name='add_brand'),
    path('add-category-brand/', views.add_category_and_brand, name='add_category_and_brand'),
    path('upload-products/', views.upload_products, name='upload_products'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('current_month_summary', views.current_month_summary, name='current_month_summary'),
    path('summary/<int:year>/<int:month>/', views.past_month_data, name='past_month_data'),
    
    
    
]