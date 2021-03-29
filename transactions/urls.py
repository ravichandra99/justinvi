from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('suppliers/', views.SupplierListView.as_view(), name='suppliers-list'),
    path('suppliers/new', views.SupplierCreateView.as_view(), name='new-supplier'),
    path('suppliers/<pk>/edit', views.SupplierUpdateView.as_view(), name='edit-supplier'),
    path('suppliers/<pk>/delete', views.SupplierDeleteView.as_view(), name='delete-supplier'),
    path('suppliers/<name>', views.SupplierView.as_view(), name='supplier'),

    path('purchases/', views.PurchaseView.as_view(), name='purchases-list'), 
    path('purchases/new', views.SelectSupplierView.as_view(), name='select-supplier'), 
    path('purchases/new/<pk>', views.PurchaseCreateView.as_view(), name='new-purchase'),    
    path('purchases/<pk>/delete', views.PurchaseDeleteView.as_view(), name='delete-purchase'),
    
    path('sales/', views.SaleView.as_view(), name='sales-list'),
    path('sales/new', views.SaleCreateView.as_view(), name='new-sale'),
    path('sales/<pk>/delete', views.SaleDeleteView.as_view(), name='delete-sale'),

    path("purchases/<billno>", views.PurchaseBillView.as_view(), name="purchase-bill"),
    path("sales/<billno>", views.SaleBillView.as_view(), name="sale-bill"),

    path('dealers/', views.DealerListView.as_view(), name='dealers-list'),
    path('dealers/new', views.DealerCreateView.as_view(), name='new-dealer'),
    path('dealers/select', views.SelectDealerView.as_view(), name='dealer-select'),
    path('sales/new/<pk>', views.SalesCreateView.as_view(), name='new-sales'),
    path('dealers/<pk>/edit', views.DealerUpdateView.as_view(), name='edit-dealer'),
    path('dealers/<pk>/delete', views.DealerDeleteView.as_view(), name='delete-dealer'),
    path('dealers/<name>', views.DealerView.as_view(), name='dealer'),
    path('daysale/',views.DaysaleView.as_view(), name = 'daysale'),
    path('daysalelist/',views.DaySaleList.as_view(), name = 'daysalelist'),
    path('datewise/',views.date_wise,name = 'date_wise'),
    
]