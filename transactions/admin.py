from django.contrib import admin
from .models import (
    Supplier, 
    PurchaseBill, 
    PurchaseItem,
    PurchaseBillDetails, 
    SaleBill, 
    SaleItem,
    SaleBillDetails,
    Dealer,
    EverydaySale
)

admin.site.register(Supplier)
admin.site.register(Dealer)
admin.site.register(PurchaseBill)
admin.site.register(PurchaseItem)
admin.site.register(PurchaseBillDetails)
admin.site.register(SaleBill)
admin.site.register(SaleItem)
admin.site.register(SaleBillDetails)
admin.site.register(EverydaySale)

admin.site.site_header = "AMR Distributors"
admin.site.site_title = "AMR Distributors"