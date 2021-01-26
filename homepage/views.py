from django.shortcuts import render
from django.views.generic import View, TemplateView
from inventory.models import Stock
from transactions.models import SaleBill, PurchaseBill, SaleBillDetails, PurchaseBillDetails
from django.db.models import Sum


class HomeView(View):
    template_name = "home.html"
    def get(self, request):        
        labels = []
        data = []        
        stockqueryset = Stock.objects.filter(is_deleted=False).order_by('-quantity')
        for item in stockqueryset:
            labels.append(item.name)
            data.append(item.quantity)
        sales = SaleBill.objects.order_by('-time')[:3]
        purchases = PurchaseBill.objects.order_by('-time')[:3]
        try:
            s = SaleBillDetails.objects.aggregate(Sum('total'))['total__sum']
            p = PurchaseBillDetails.objects.aggregate(Sum('total'))['total__sum']
        except:
            p = 0
            s = 0
        print(p,s)
        if p is None:
            p = 0
        pol = s - p
        context = {
            'labels'    : labels,
            'data'      : data,
            'sales'     : sales,
            'purchases' : purchases,
            'pol'       : pol,
            's' : s,
            'p' : p
        }
        return render(request, self.template_name, context)

class AboutView(TemplateView):
    template_name = "about.html"