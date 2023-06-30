"""
URL configuration for warehouse_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from product.views import add_purchase_order_view,add_checked_stock_view,web_scrap_product_data,po_stock_check_view,store_sale_view
from accounts.views import account_transaction_view,account_display_view


urlpatterns = [
    path('product/add-purchase-order/', add_purchase_order_view),
    path('product/po-stock-checking/', po_stock_check_view),
    path('product/add-checked-stock/', add_checked_stock_view),
    path('product/store-sale/', store_sale_view),
    path('product/add-checked-stock/<str:product_id>', web_scrap_product_data),
    path('accounts/account-transaction/', account_transaction_view),
    path('accounts/account-display/', account_display_view),
    path('admin/', admin.site.urls),
]
