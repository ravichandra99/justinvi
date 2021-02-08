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
    path('ajax/barcode',views.get_barcode, name ='get_barcode'),
]