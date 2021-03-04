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
        if not request.user.is_superuser:        
            stockqueryset = Stock.objects.filter(is_deleted=False).order_by('-quantity')
        else:
            stockqueryset = Stock.objects.filter(super_market__user = request.user).filter(is_deleted=False).order_by('-quantity')
        for item in stockqueryset:
            labels.append(item.name)
            data.append(item.quantity)
        if not request.user.is_superuser:
            sales = SaleBill.objects.order_by('-time')[:3]
            purchases = PurchaseBill.objects.order_by('-time')[:3]
        else:
            a = SaleBill()
            b = PurchaseBill()
            sales = a.get_smsale_list(self.request.user)[:3]
            purchases = b.get_smpurchase_list(self.request.user)[:3]

        try:
            sList = [i.total for i in SaleBillDetails.objects.all() if i.total is not None and i.total != '']
            pList = [i.total for i in PurchaseBillDetails.objects.all() if i.total is not None and i.total != '']
            print(sList,pList)
            sfloat = [float(i) for i in sList]
            pfloat = [float(i) for i in pList]
            s = sum(sfloat)
            p = sum(pfloat)

        except:
            s = 0
            p = 0

        pol = s - p

        context = {
            'labels'    : labels,
            'data'      : data,
            'sales'     : sales,
            'purchases' : purchases,
            'pol'       : round(pol,2),
            's' : s,
            'p' : p
        }
        return render(request, self.template_name, context)

class AboutView(TemplateView):
    template_name = "about.html"