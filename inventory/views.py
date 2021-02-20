from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View,
    CreateView, 
    UpdateView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Stock,SuperMarket
from .forms import StockForm
from django_filters.views import FilterView
from .filters import StockFilter
from django.http import JsonResponse


class StockListView(FilterView):
    filterset_class = StockFilter
    # queryset = Stock.objects.filter(is_deleted=False)
    template_name = 'inventory.html'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Stock.objects.filter(is_deleted = False)
        else:
            return Stock.objects.filter(is_deleted = False).filter(super_market__user = self.request.user)


class StockCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Stock                                                                       # setting 'Stock' model as model
    form_class = StockForm                                                              # setting 'StockForm' form as form
    template_name = "edit_stock.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Stock has been created successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Stock'
        context["savebtn"] = 'Add to Inventory'
        context['form'].fields['super_market'].queryset = SuperMarket.objects.filter(user = self.request.user)
        return context       


class StockUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
    model = Stock                                                                       # setting 'Stock' model as model
    form_class = StockForm                                                              # setting 'StockForm' form as form
    template_name = "edit_stock.html"                                                   # 'edit_stock.html' used as the template
    success_url = '/inventory'                                                          # redirects to 'inventory' page in the url after submitting the form
    success_message = "Stock has been updated successfully"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Stock'
        context["savebtn"] = 'Update Stock'
        context["delbtn"] = 'Delete Stock'
        return context


class StockDeleteView(View):                                                            # view class to delete stock
    template_name = "delete_stock.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Stock has been deleted successfully"                             # displays message when form is submitted
    
    def get(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        return render(request, self.template_name, {'object' : stock})

    def post(self, request, pk):  
        stock = get_object_or_404(Stock, pk=pk)
        stock.is_deleted = True
        stock.save()                                               
        messages.success(request, self.success_message)
        return redirect('inventory')

def get_costprice(request):
    barcode = request.GET.get('barcode')
    if Stock.objects.filter(barcode = barcode).filter(super_market__user = request.user).exists():
        stock = Stock.objects.filter(barcode = barcode).filter(super_market__user = request.user)[0]
        if stock.super_market.user == request.user:
            name = stock.name
            cost_price = stock.cost_price
            data = {'cost_price':cost_price, 'name':name}
            return JsonResponse(data)

def get_sellingprice(request):
    barcode = request.GET.get('barcode')
    if Stock.objects.filter(barcode = barcode).filter(super_market__user = request.user).exists():
        stock = Stock.objects.filter(barcode = barcode).filter(super_market__user = request.user)[0]
        if stock.super_market.user == request.user:
            name=stock.name
            selling_price = stock.selling_price
            data = {'selling_price':selling_price, 'name':name}
            return JsonResponse(data)

def get_stock(request):
    stock = request.GET.get('stock')
    stocks = Stock.objects.filter(name__startswith = stock).filter(super_market__user = request.user)
    print(stocks)
    return render(request, 'sales/stock_list.html', {'stocks': stocks})

def get_barcode_cp(request):
    stock = request.GET.get('stock')
    if Stock.objects.filter(name = stock).filter(super_market__user = request.user).exists():
        juststock = Stock.objects.filter(name = stock).filter(super_market__user = request.user)[0]
        if juststock.super_market.user == request.user:
            barcode = juststock.barcode
            price = juststock.cost_price
        else:
            barcode = 'NOT YET'
            price = 0
    else:
        barcode = 'NOT YET'
        price = 0
    data = {'barcode':barcode , 'price' : price}
    return JsonResponse(data)

def get_barcode_sp(request):
    print('im barcode')
    stock = request.GET.get('stock')
    print(stock)
    actualstock = stock.split('@')[0]
    supplier_name = request.GET.get('supplier_name')
    print(Stock.objects.filter(name = actualstock).exists())
    if Stock.objects.filter(name = actualstock).filter(super_market__user = request.user.id).exists():
        juststock = Stock.objects.filter(name = stock).filter(super_market__user = request.user.id).filter(supplier_name = supplier_name)[0]
        print(juststock)
        # barcodes = [i.barcode for i in juststock if i.super_market.user == request.user]
        # prices = [i.selling_price for i in juststock if i.super_market.user == request.user]
        # supplier_names = [i.supplier_name for i in juststock if i.super_market.user == request.user]
        # stocks = [i.name for i in juststock if i.super_market.user == request.user]
        if juststock.super_market.user == request.user:
            barcode = juststock.barcode
            price = juststock.selling_price
        else:
            barcode = 'NOT YET'
            price = 0
            supplier_name = 'NONE'
            stock = 'NONE'
    else:
        barcode = 'NOT YET'
        price = 0
        supplier_name = 'NONE'
        stock = 'NONE'
    data = {'barcode' : barcode , 'price' : price, 'supplier_name' : supplier_name, 'stock' : stock}
    return JsonResponse(data)

