from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import (
    View, 
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    PurchaseBill, 
    Supplier, 
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,  
    SaleItem,
    SaleBillDetails,
    Dealer,
    EverydaySale
)
from .forms import (
    SelectSupplierForm, 
    PurchaseItemFormset,
    PurchaseDetailsForm, 
    SupplierForm, 
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm,
    SelectDealerForm,
    DealerForm,
    DiscountForm
)
from inventory.models import Stock,SuperMarket
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from datetime import date
# shows a lists of all suppliers
class SupplierListView(ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    queryset = Supplier.objects.filter(is_deleted=False)
    paginate_by = 10


# used to add a new supplier
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier has been created successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Supplier'
        context["savebtn"] = 'Add Supplier'
        return context     


# used to update a supplier's info
class SupplierUpdateView(SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier details has been updated successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Supplier'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Supplier'
        return context


# used to delete a supplier
class SupplierDeleteView(View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "Supplier has been deleted successfully"

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object' : supplier})

    def post(self, request, pk):  
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.save()                                               
        messages.success(request, self.success_message)
        return redirect('suppliers-list')


# used to view a supplier's profile
class SupplierView(View):
    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier'  : supplierobj,
            'bills'     : bills
        }
        return render(request, 'suppliers/supplier.html', context)




# shows the list of bills of all purchases 
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs =  PurchaseBill.objects.all().order_by('-time')
        else:
            a = PurchaseBill()
            qs = a.get_smpurchase_list(self.request.user)
            print(qs)
        return qs


# used to select the supplier
class SelectSupplierView(View):
    form_class = SelectSupplierForm
    template_name = 'purchases/select_supplier.html'

    def get(self, request, *args, **kwargs):                                    # loads the form page
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):                                   # gets selected supplier and redirects to 'PurchaseCreateView' class
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get("supplier")
            supplier = get_object_or_404(Supplier, id=supplierid)
            return redirect('new-purchase', supplier.pk)
        return render(request, self.template_name, {'form': form})


# used to generate a bill object and save items
class PurchaseCreateView(View):                                                 
    template_name = 'purchases/new_purchase.html'

    def get(self, request, pk):
        formset = PurchaseItemFormset(request.GET or None)                      # renders an empty formset
        supplierobj = get_object_or_404(Supplier, pk=pk)                        # gets the supplier object
        context = {
            'formset'   : formset,
            'supplier'  : supplierobj,
        }                                                                       # sends the supplier and formset as context
        return render(request, self.template_name, context)

    def post(self, request, pk):

        formset = PurchaseItemFormset(request.POST)                             # recieves a post method for the formset
        supplierobj = get_object_or_404(Supplier, pk=pk)                        # gets the supplier object
        if formset.is_valid():
            # saves bill
            billobj = PurchaseBill(supplier=supplierobj)                        # a new object of class 'PurchaseBill' is created with supplier field set to 'supplierobj'
            billobj.save()                                                      # saves object into the db
            # create bill details object
            billdetailsobj = PurchaseBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:                                                # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj                                      # links the bill object to the items
                # gets the stock item
                if Stock.objects.filter(barcode=billitem.barcode).filter(super_market__user = request.user).exists():
                    stock = Stock.objects.filter(barcode=billitem.barcode).filter(super_market__user = request.user)[0]       # gets the item
                billitem.stock = stock
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity += billitem.quantity                              # updates quantity
                # saves bill item and stock
                stock.save()
                billitem.save()
            messages.success(request, "Purchased items have been registered successfully")
            return redirect('purchase-bill', billno=billobj.billno)
        formset = PurchaseItemFormset(request.GET or None)
        context = {
            'formset'   : formset,
            'supplier'  : supplierobj
        }
        return render(request, self.template_name, context)


# used to delete a bill object
class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "purchases/delete_purchase.html"
    success_url = '/transactions/purchases'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Purchase bill has been deleted successfully")
        return super(PurchaseDeleteView, self).delete(*args, **kwargs)




# shows the list of bills of all sales 
class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs =  SaleBill.objects.all().order_by('-time')
        else:
            a = SaleBill()
            qs = a.get_smsale_list(self.request.user)
            print(qs)
        return qs


# used to generate a bill object and save items
class SaleCreateView(View):                 
    template_name = 'sales/new_sale.html'

    def get(self, request):
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)                          # renders an empty formset
        stocks = Stock.objects.filter(is_deleted=False)
        context = {
            'form'      : form,
            'formset'   : formset,
            'stocks'    : stocks
        }
        return render(request, self.template_name, context)

    def post(self, request):
        print(request.POST)                
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)                                 # recieves a post method for the formset
        if form.is_valid() and formset.is_valid():
            # saves bill
            billobj = form.save(commit=False)
            billobj.save()
            print(billobj)     
            # create bill details object
            billdetailsobj = SaleBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:                                                # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj                                       # links the bill object to the items
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)      
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity -= billitem.quantity   
                # saves bill item and stock
                stock.save()
                billitem.save()
            messages.success(request, "Sold items have been registered successfully")
            return redirect('sale-bill', billno=billobj.billno)
        form = SaleForm(request.GET or None)
        discount_form = DiscountForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        context = {
            'discount_form' : discount_form,
            'form'      : form,
            'formset'   : formset,
        }
        return render(request, self.template_name, context)


# used to delete a bill object
class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transactions/sales'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Sale bill has been deleted successfully")
        return super(SaleDeleteView, self).delete(*args, **kwargs)




# used to display the purchase bill object
class PurchaseBillView(View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        bill = PurchaseBill.objects.get(billno=billno)
        items = PurchaseItem.objects.filter(billno=billno)
        billdetails = PurchaseBillDetails.objects.get(billno=billno)
        sgst_amount = [i.totalprice * i.stock.sgst/100 for i in items]
        cgst_amount = [i.totalprice * i.stock.cgst/100 for i in items]
        total_amount = [round(i.totalprice ,2) for i in items]
        amt_details = list(zip(sgst_amount,cgst_amount,total_amount))
        total = round(sum(total_amount),2)
        billdetails.total = total
        billdetails.save()
        context = {
            'bill'          : bill,
            'items'         : list(zip(items,sgst_amount,cgst_amount,total_amount)),
            'billdetails'   : billdetails,
            'bill_base'     : self.bill_base,
            'total'         : total,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = PurchaseBillDetails.objects.get(billno=billno)
            
            billdetailsobj.eway = request.POST.get("eway")    
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("sgst")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill'          : PurchaseBill.objects.get(billno=billno),
            'items'         : PurchaseItem.objects.filter(billno=billno),
            'billdetails'   : PurchaseBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)


# used to display the sale bill object
class SaleBillView(View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"
    
    def get(self, request, billno):
        bill = SaleBill.objects.get(billno=billno)
        items = SaleItem.objects.filter(billno=billno)
        billdetails = SaleBillDetails.objects.get(billno=billno)
        sgst_amount = [i.totalprice * i.stock.sgst/100 for i in items]
        cgst_amount = [i.totalprice * i.stock.cgst/100 for i in items]
        total_amount = [round(i.totalprice ,2) for i in items]
        amt_details = list(zip(sgst_amount,cgst_amount,total_amount))
        total = round(sum(total_amount),2)
        discount = float(billdetails.tcs)
        billdetails.igst = date.today()
        total_after_discount = total - (total * discount / 100)

        billdetails.cess = total
        billdetails.total = total_after_discount
        billdetails.save()
        supermarket = SuperMarket.objects.get(user = request.user)

        context = {
            'bill'          : bill,
            'items'         : list(zip(items,sgst_amount,cgst_amount,total_amount)),
            'billdetails'   : billdetails,
            'bill_base'     : self.bill_base,
            'total'         : total,
            'total_sgst' : sum(sgst_amount),
            'total_cgst' : sum(cgst_amount),
            'supermarket' : supermarket,
            'discount' : discount
            # 'undupesgst' : list(set([i.stock.sgst for i in items])),
            # 'undupecgst' : list(set([i.stock.cgst for i in items])),
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            print(request.POST)
            billdetailsobj = SaleBillDetails.objects.get(billno=billno)
            
            billdetailsobj.eway = request.POST.get("eway")    
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("sgst")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            supermarket = SuperMarket.objects.get(user = request.user)
            print(supermarket.name,supermarket.gstno)
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill'          : SaleBill.objects.get(billno=billno),
            'items'         : SaleItem.objects.filter(billno=billno),
            'billdetails'   : SaleBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
            'supermarket'   : supermarket
        }
        return render(request, self.template_name, context)

class DealerView(View):
    def get(self, request, name):
        dealerobj = get_object_or_404(Dealer, name=name)
        bill_list = SaleBill.objects.filter(dealer=dealerobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'dealer'  : dealerobj,
            'bills'     : bills
        }
        return render(request, 'dealers/dealer.html', context)

# shows a lists of all dealers
class DealerListView(ListView):
    model = Dealer
    template_name = "dealers/dealers_list.html"
    queryset = Dealer.objects.filter(is_deleted=False)
    paginate_by = 10


# used to add a new dealer
class DealerCreateView(SuccessMessageMixin, CreateView):
    model = Dealer
    form_class = DealerForm
    success_url = '/transactions/dealers'
    success_message = "Dealer has been created successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Dealer'
        context["savebtn"] = 'Add Dealer'
        return context  


# used to update a dealers's info
class DealerUpdateView(SuccessMessageMixin, UpdateView):
    model = Dealer
    form_class = DealerForm
    success_url = '/transactions/dealers'
    success_message = "Dealer details has been updated successfully"
    template_name = "dealers/edit_dealer.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Dealer'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Dealer'
        return context

# used to delete a supplier
class DealerDeleteView(View):
    template_name = "dealers/delete_dealer.html"
    success_message = "Dealer has been deleted successfully"

    def get(self, request, pk):
        dealer = get_object_or_404(Dealer, pk=pk)
        return render(request, self.template_name, {'object' : dealer})

    def post(self, request, pk):  
        dealer = get_object_or_404(Dealer, pk=pk)
        dealer.is_deleted = True
        dealer.save()                                               
        messages.success(request, self.success_message)
        return redirect('dealers-list')


# used to delete a supplier
class SupplierDeleteView(View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "Supplier has been deleted successfully"

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object' : supplier})

    def post(self, request, pk):  
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.save()                                               
        messages.success(request, self.success_message)
        return redirect('suppliers-list')


# used to view a supplier's profile
class SupplierView(View):
    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier'  : supplierobj,
            'bills'     : bills
        }
        return render(request, 'suppliers/supplier.html', context)

# used to select the supplier
class SelectDealerView(View):
    form_class = SelectDealerForm
    template_name = 'sales/select_dealer.html'

    def get(self, request, *args, **kwargs):                                    # loads the form page
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):                                   # gets selected supplier and redirects to 'PurchaseCreateView' class
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get("dealer")
            supplier = get_object_or_404(Dealer, id=supplierid)
            return redirect('new-sales', supplier.pk)
        return render(request, self.template_name, {'form': form})

class SalesCreateView(View):                                                 
    template_name = 'sales/new_sale.html'

    def get(self, request, pk):
        formset = SaleItemFormset(request.GET or None)                      # renders an empty formset
        supplierobj = get_object_or_404(Dealer, pk=pk)                        # gets the supplier object
        context = {
            'formset'   : formset,
            'supplier'  : supplierobj,
        }                                                                       # sends the supplier and formset as context
        return render(request, self.template_name, context)

    def post(self, request, pk):
        # print(request.POST.get('discount'))
        formset = SaleItemFormset(request.POST)                             # recieves a post method for the formset
        supplierobj = get_object_or_404(Dealer, pk=pk)                       # gets the supplier object
        if formset.is_valid():
            # saves bill
            billobj = SaleBill(dealer=supplierobj)                        # a new object of class 'PurchaseBill' is created with supplier field set to 'supplierobj'
            billobj.save()                                                      # saves object into the db
            # create bill details object
            billdetailsobj = SaleBillDetails(billno=billobj)
            billdetailsobj.tcs = request.POST.get('discount')
            billdetailsobj.save()
            for form in formset:                                                # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj
                print(billitem.barcode)                                  # links the bill object to the items
                # gets the stock item
                if Stock.objects.filter(barcode=billitem.barcode).filter(super_market__user = request.user).exists():
                    stock = Stock.objects.filter(barcode=billitem.barcode).filter(super_market__user = request.user)[0]
                print(stock)      # gets the item
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                sm = ''
                if stock.quantity <= 0:
                    #messages.success(request, "WOW STOCK EMPTY.!")
                    #return render(request,'nostock.html')
                    sm = "{} has no stock please add in inventory".format(stock.name)
                stock.quantity -= billitem.quantity  
                billitem.stock = stock                            # updates quantity
                # saves bill item and stock
                stock.save()
                billitem.save()
            messages.success(request, "Sold items have been registered successfully {}".format(sm))
            return redirect('sale-bill', billno=billobj.billno)
        formset = SaleItemFormset(request.GET or None)
        context = {
            'formset'   : formset,
            'supplier'  : supplierobj
        }
        return render(request, self.template_name, context)

class DaysaleView(CreateView):
    model = EverydaySale
    fields = '__all__'
    template_name = 'sales/day_sale.html'
    success_url = '/transactions/daysalelist/'

    def get_form(self,form_class = None):
        form = super(DaysaleView, self).get_form(form_class)
        form.fields['super_market'].widget.attrs.update({'class': 'textinput form-control'})
        form.fields['supplier_name'].widget.attrs.update({'class': 'textinput form-control'})
        form.fields['amount'].widget.attrs.update({'class': 'textinput form-control amount', 'min': '0', 'required': 'true'})
        form.fields['date'].widget.attrs.update({'class': 'textinput form-control'})


        return form

    def post(self, request, *args, **kwargs):
        # super().post() maybe raise a ValidationError if it is failure to save
        try:
            response = super().post(request, *args, **kwargs)
        except:
            messages.info(request, 'UNIQUE constraint failed.')
            response = redirect('daysale')
        # the below code is optional. django has responsed another erorr message
        return response
        

class DaySaleList(ListView):
    model = EverydaySale
    template_name = "sales/everyday_list.html"
    context_object_name = 'everyday_list'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs = EverydaySale.objects.all().order_by('-date')
        else:
            qs = EverydaySale.objects.filter(super_market__user = self.request.user).order_by('-date')
        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        qs = context['everyday_list']
        total_amount = qs.aggregate(Sum('amount'))
        context['total'] = total_amount['amount__sum']
        return context

def date_wise(request):
    date_wise = [i.igst for i in SaleBillDetails.objects.all()]
    date_wise = list(dict.fromkeys(date_wise))
    print(date_wise)
    for i in SaleBillDetails.objects.all():
        if i.total is None:
            i.total = 0
            i.save()
    saleitems = SaleItem.objects.filter(stock__super_market__user = request.user).values_list('billno', flat = True)
    if request.user.is_superuser:
        date_price = [(i,sum([round(float(i.total),2) for i in SaleBillDetails.objects.filter(igst = i)])) for i in date_wise]
    else:
        date_price = [(i,sum([round(float(i.total),2) for i in SaleBillDetails.objects.filter(igst = i).filter(billno__in = saleitems)])) for i in date_wise]
    print(date_price)
    return render(request,'bill/date_wise.html',{'date_price':date_price})



