from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='inventory'),
    path('new', views.StockCreateView.as_view(), name='new-stock'),
    path('stock/<pk>/edit', views.StockUpdateView.as_view(), name='edit-stock'),
    path('stock/<pk>/delete', views.StockDeleteView.as_view(), name='delete-stock'),
    path('ajax/costprice',views.get_costprice, name ='get_costprice'),
    path('ajax/sellingprice',views.get_sellingprice, name ='get_sellingprice'),
    path('ajax/stock',views.get_stock, name ='get_stock'),
    path('ajax/barcodecp',views.get_barcode_cp, name ='get_barcode_cp'),
    path('ajax/barcodesp',views.get_barcode_sp, name ='get_barcode_sp'),
    path('ajax/barcodedd',views.get_barcode_dropdown, name ='get_barcode_dropdown'),
    path('ajax/stocksp',views.get_stock_sp, name ='get_stock_sp'),
]