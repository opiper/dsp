from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F, Case, When, Value, CharField
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext as _

from StockManager.models import Company, Product, Stock, StockChange
from StockManager.views import Stock_In_Function, modify_stock
from warehouse.views import is_worker, todayDate

from .models import LabelChangeService, ServiceHistory, ServiceList


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewServices(request):

    services = ServiceList.objects.all()

    return render(request, 'ServiceManager/viewServices.html', {'services':services})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewServiceHistoryStock(request):
    id = request.GET.get('id')
    product = Product.objects.get(id=id)

    service_histories_ids = ServiceHistory.objects.filter(
        product=product
    ).values_list('id', flat=True)

    label_change_services_ids = LabelChangeService.objects.filter(
        product=product
    ).exclude(
        product=F('newProduct')
    ).values_list('id', flat=True)

    # Combine IDs and remove duplicates
    combined_ids = list(set(service_histories_ids.union(label_change_services_ids)))

    preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(combined_ids)])
    service_histories_full = ServiceHistory.objects.filter(
        id__in=combined_ids
    ).annotate(
        order=preserved_order
    ).select_related(
        'product', 'serviceType', 'agent'
    ).order_by('order')

    return render(request, 'ServiceManager/viewServiceHistoryStock.html',{'services':service_histories_full})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def addService(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = float(request.POST.get('price'))

        ServiceList.objects.create(name=name, unitPrice=price)
        return redirect('viewServices')
    else:
        return render(request, 'ServiceManager/addService.html')


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def editServices(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        service = ServiceList.objects.get(id=id)
        return render(request, 'ServiceManager/editServices.html', {'service':service})

    else:
        id = request.POST.get('id')
        price = float(request.POST.get('price'))

        ServiceList.objects.filter(id=id).update(unitPrice=price)
        return redirect('viewServices')


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def labelChange(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')
        label = request.POST.get('label', '').upper().replace(' ', '')
        quantity = int(request.POST.get('number', 0))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Error: Product not found.'})
        
        if product.stockType == 'CA':
            return JsonResponse({'status': 'error', 'message': 'Error: Cannot change Label of Carton.'})
        
        skus = Stock.objects.filter(product=product, active=1).order_by('inDate')
        skuQuantity = len(skus) or 0

        if skuQuantity < quantity:
            return JsonResponse({'status': 'error', 'message': 'Error: Not enough stock.'})
        
        newProduct, created = Product.objects.get_or_create(
            productId=label, stockType=product.stockType, sizeCbm=product.sizeCbm,
            unitPrice=product.unitPrice, company=product.company
        )

        if Stock_In_Function(request, newProduct.productId, product.company, quantity, todayDate(), product.stockType, product.sizeCbm, product.unitPrice, '', skus[0].location) == 'Success':
            for i in range(quantity):
                skus[i].active = 0
                skus[i].outDate = todayDate()
                skus[i].save()
            LabelChangeService.objects.create(product=product,newProduct=newProduct,serviceType=ServiceList.objects.get(name='Label Change'),\
                                              quantity=quantity,date=todayDate(),agent=request.user)

            StockChange.objects.bulk_create([
                StockChange(category='O', quantity=quantity, date=todayDate(), agent=request.user,  product=product),
                StockChange(category='I', quantity=quantity, date=todayDate(), agent=request.user,  product=newProduct)
            ])
            
            return JsonResponse({'status': 'success', 'message': _('Success: Changed label on %(product)s to %(newProduct)s') % {'product': product.productId, 'newProduct': newProduct.productId}})
        
        else:
            return JsonResponse({'status': 'error', 'message': 'Error: Failed to change label.'})
    
    else:
        return redirect('home')


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def assorting(request):
    if request.method == 'POST':
        id = request.POST.get('id', 0)
        quantity = request.POST.get('quantity', 0)
        label = request.POST.get('label', '')
        sizeCbm = request.POST.get('sizeCbm', 0)
        unitPrice = request.POST.get('unitPrice', 0)

        if quantity == 0 or id == 0 or sizeCbm == 0 or unitPrice == 0:
            return JsonResponse({'status': 'error', 'message': 'Error: Quantity or ID cannot be 0.'})
        elif label == '':
            return JsonResponse({'status': 'error', 'message': 'Error: Label cannot be empty.'})
        
        product = Product.objects.get(id=id)
        service = ServiceList.objects.get(name='Assorting')

        ServiceHistory.objects.create(product=product,serviceType=service,\
                                    quantity=quantity,date=todayDate(),agent=request.user)
        
        newProduct, created = Product.objects.get_or_create(
            productId=label, stockType='SK', sizeCbm=product.sizeCbm,
            unitPrice=product.unitPrice, company=product.company
        )
        
        if Stock_In_Function(request, newProduct.productId, product.company, quantity, todayDate(), 'SK', sizeCbm, unitPrice, '', '') == 'Success':  
            StockChange.objects.create(category='I', quantity=quantity, date=todayDate(),\
                                        agent=request.user,  product=newProduct)
            product.active = 0
            product.save()

            return JsonResponse({'status': 'success', 'message': _('Success: %(quantity)d SKUs have been moved to %(label)s') % {'quantity': quantity, 'label': label}})
        else:
            return JsonResponse({'status': 'error', 'message': 'Error: Failed to move SKUs.'})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def changeCard(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=request.POST.get('id', 0))
        quantity = int(request.POST.get('quantity', 0))
        service = ServiceList.objects.get(name='Change Card')

        ServiceHistory.objects.create(product=product,serviceType=service,\
                                    quantity=quantity,date=todayDate(),agent=request.user)

        return JsonResponse({'status': 'success', 'message': _('Success: %(quantity)d SKUs have had their cards changed') % {'quantity': quantity}})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def clearance(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=request.POST.get('id', 0))
        quantity = int(request.POST.get('quantity', 0))
        if product.company.companyName == 'Thinkobox':
            if modify_stock(request, product.id, quantity, 'SK', 'decrease') == 'Success':
                ServiceHistory.objects.create(product=product, serviceType=ServiceList.objects.get(name='Clearance'), quantity=int(request.POST.get('quantity', 0)), price=0, date=todayDate(), agent=request.user)
                return JsonResponse({'status': 'success', 'message': _('Success: %(quantity)d SKUs have been cleared') % {'quantity': quantity}})
            else:
                return JsonResponse({'status': 'error', 'message': 'Error: Not enough stock to clear'})
        else:
            stockList = Stock.objects.filter(product=product).filter(stockType='SK').order_by('-date,id')
            sku = stockList[0]
            service = ServiceList.objects.get(name='Clearance')

            if modify_stock(request,product.id,quantity,'SK','decrease') == 'Success':
                newProduct = Product.objects.get_or_create(productId=product.productId+'_thinkobox',company=Company.objects.get(companyName='thinkobox'))
                if Stock_In_Function(request,newProduct.id,Company.objects.get(name='Thinkobox'),\
                                      quantity,todayDate(),product.sizeCbm,product.unitPrice,\
                                        '', sku.location) == 'Success':
                    ServiceHistory.objects.create(stock=product,serviceType=service,quantity=quantity,\
                                                date=todayDate(),agent=request.user)
                    StockChange.objects.create(category='I',type='SK',quantity=quantity,agent=request.user,\
                                                date=todayDate(),product=newProduct[0])
                    return JsonResponse({'status': 'success', 'message': _('Success: %(quantity)d SKUs have been cleared') % {'quantity': quantity}})

            else:
                return JsonResponse({'status': 'error', 'message': 'Error: Not enough stock to clear'})
                


## Calls StockOut function to move number of SKUs out and record service history.
@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def destroy(request):
    if request.method == 'POST':
        id = request.POST.get('id', 0)
        quantity = int(request.POST.get('quantity', 0))

        product = Product.objects.get(id=id)
        service = ServiceList.objects.get(name='Destroy')

        if modify_stock(request,id,quantity,'SK','decrease') == 'Success':

            ServiceHistory.objects.create(product=product,serviceType=service,\
                                        quantity=quantity,date=todayDate(),agent=request.user)
            
            return JsonResponse({'status': 'success', 'message': _('Success: %(quantity)d SKUs have been destroyed') % {'quantity': quantity}})
        else:
            return JsonResponse({'status': 'error', 'message': 'Error: Failed to destroy SKUs.'})
        

def container(request):
    return render(request, 'ServiceManager/container.html')
    

@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def inspection(request):
    if request.method == 'POST':
        id = request.POST.get('id', 0)
        quantity = request.POST.get('quantity', 0)

        if quantity == 0 or id == 0:
            return JsonResponse({'status': 'error', 'message': 'Error: Quantity or ID cannot be 0.'})
        
        product = Product.objects.get(id=id)
        service = ServiceList.objects.get(name='Inspection')

        ServiceHistory.objects.create(product=product,serviceType=service,\
                                    quantity=quantity,date=todayDate(),agent=request.user)

        return JsonResponse({'status': 'success', 'message': _('Success: %(quantity)d SKUs have been inspected') % {'quantity': quantity}})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def photo(request):
    if request.method == 'POST':
        id = request.POST.get('id', 0)
        quantity = int(request.POST.get('quantity', 0))

        if quantity == 0 or id == 0:
            return JsonResponse({'status': 'error', 'message': 'Error: Quantity or ID cannot be 0.'})

        product = Product.objects.get(id=id)
        service = ServiceList.objects.get(name='Photo')

        ServiceHistory.objects.create(product=product,serviceType=service,\
                                    quantity=quantity,date=todayDate(),agent=request.user)

        return JsonResponse({'status': 'success', 'message': _('Success: %(quantity)d photos taken on %(product)s') % {'product': product.productId, 'quantity': quantity}})

    else:
        return redirect('home')