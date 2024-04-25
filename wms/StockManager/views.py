import codecs
import csv

import numpy as np
from model import scratch

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.db.models import Q
from django.http import JsonResponse

from CompanyManager.models import Company
from CourierManager.models import CourierOption
from warehouse.views import (display_error, display_success, is_worker,
                             todayDate)
from wms.model import easyish

from .forms import AddStockForm, CSVUploadForm
from .models import Product, Stock, StockChange, StockDispatch, DispatchItems

# Define dictionaries for size-related calculations
__cbm_dict__ = {'SK': {'SM': 0.002, 'ME': 0.01, 'LA': 0.1},
            'CA': {'SM': 0.03, 'ME': 0.06, 'LA': 0.12}}
__price_dict__ = {'SK': {'SM': 0.002, 'ME': 0.01, 'LA': 0.1},
              'CA': {'SM': 1, 'ME': 1, 'LA': 1}}


# Function to handle stock modification
def modify_stock(request, product, quantity, stock_type, action):
    stock_list = Stock.objects.filter(product=product, stockType=stock_type).order_by('-date')
    total_stock = len(stock_list)

    if action == 'increase':
        # Handle stock increase
        Stock_In_Function(request, product.productId, product.company, quantity, todayDate(),
                          stock_type, stock_list[0].size, stock_list[0].unitCbm, 'IN',
                          stock_list[0].unitPrice, stock_list[0].notes, stock_list[0].location)
        StockChange.objects.create(category='I', type=stock_type, quantity=quantity,
                                    agent=request.user, date=todayDate(), product=product)
    
    elif action == 'decrease':
        # Handle stock decrease
        if total_stock <= quantity:
            return 'Error'
        for i in range(quantity):
            stock_list[i].active = False
            stock_list[i].save()
            StockChange.objects.create(category='O', type=stock_type, quantity=quantity,
                                    agent=request.user, date=todayDate(), product=product)
    
    return 'Success'


def Stock_In_Function(request, id, company, quantity, date, stockType, sizeCbm, unitPrice, notes, location):
    # Create Stock entries for incoming stock
    product, created = Product.objects.get_or_create(productId=id, stockType=stockType, company=company)
    if created:
        product.sizeCbm = sizeCbm
        product.unitPrice = unitPrice
        product.save()
    if stockType == 'SK':
        stockList = []
        batchId = Stock.objects.filter(product=product).values('batchId').distinct()
        batchId = len(batchId) + 1
        for i in range(quantity):
            stockList.append(Stock(inDate=date, notes=notes, location=location,
                                    batchId=batchId, agent=request.user, product=product))
        Stock.objects.bulk_create(stockList)
    else:
        stockList = []
        for i in range(quantity):
            stockList.append(Stock(stockId=f"{quantity}-{i+1}", inDate=date,
                                    notes=notes, location=location, batchId=str(id)+str(quantity),
                                    agent=request.user, product=product))
        Stock.objects.bulk_create(stockList)
    return 'Success'


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def addStock(request):
    if request.method == 'POST':
        form = AddStockForm(request.POST, initial={'size': 'SM'})

        if form.is_valid():
            # Retrieve and process form data
            product_id = request.POST.get('productId').upper().replace(' ', '')
            company = Company.objects.get(companyName=request.POST.get('company', ''))
            stock_type = request.POST.get('stockType')
            size = request.POST.get('size')
            quantity = int(request.POST.get('quantity', 0))
            date = request.POST.get('inDate')
            notes = request.POST.get('notes')
            location = request.POST.get('location').upper().replace(' ', '')

            size_cbm = __cbm_dict__[stock_type][size]
            unit_price = __price_dict__[stock_type][size]

            # Get or create the product
            product, created = Product.objects.get_or_create(productId=product_id, stockType=stock_type, company=company)

            if created:
                product.sizeCbm = size_cbm
                product.unitPrice = unit_price
                product.save()
                stock_in = Stock_In_Function(request, product_id, company, quantity, date, stock_type,
                                             size_cbm, unit_price, notes, location)
                if stock_in != 'Success':
                    display_error(request, _('Error: An error occurred'))
                    return redirect('home')
            else:
                if stock_type == 'CA':
                    display_error(request, _('Error: Cartons of that ID already exist'))
                    return redirect('home')
                else:
                    product.active = True
                    product.save()
                    stock_in = Stock_In_Function(request, product_id, company, quantity, date, stock_type,
                                                 size_cbm, unit_price, notes, location)
                    if stock_in != 'Success':
                        display_error(request, _('Error: An error occurred'))
                        return redirect('home')

            stock_change = StockChange.objects.create(category='I', quantity=quantity, date=date,
                                                      agent=request.user, product=product)
            stock_change.save()
            display_success(request, _('Success: Stock Levels Updated'))
            return redirect('home')

    else:
        form = AddStockForm()

    return render(request, 'StockManager/addStock.html', {'form': form})


## Deleting a product.
@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def deleteStock(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        product = Product.objects.get(id=id)

        stockChange = StockChange.objects.filter(product=product)
        if len(stockChange) > 1:
            product.active = False
            product.save()
            display_success(request, 'Success: Stock Entry Deleted')
            return redirect('home')
        try:
            DispatchItems.objects.get(stock__product=product)
        except ObjectDoesNotExist:
            product.delete()
        
        display_success(request, 'Success: Stock Entry Deleted')
        return redirect('home')

    return render(request, 'StockManager/deleteStock.html')


## Send Out stock from the warehouse
@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def dispatchStock(request):
    if request.method == 'GET':    
        id = request.GET.get('id')
        product = Product.objects.get(id=id)
        if product.stockType == 'SK':
            productList = Product.objects.filter(stockType='SK', active=1).order_by('productId')
            courierOptions = CourierOption.objects.all().order_by('courier').order_by('id')
            return render(request, 'StockManager/dispatchStock.html', {'product':product,'courierOptions':courierOptions,'productList':productList,'ogProduct':product})
        
        else: 
            courierOptions = CourierOption.objects.all().order_by('courier').order_by('id')
            cartonList = Stock.objects.filter(product=product, active=1)
            return render(request, 'StockManager/cartonDispatch.html', {'product':product,'courierOptions':courierOptions,'cartonList':cartonList})
    
    else:
        stockType = request.POST.get('stockType')
        if stockType == 'SK':
            static_dropdown = int(request.POST.get('static_dropdown'))  # Gets integer of ID of og product
            static_quantity = int(request.POST.get('static_quantity'))
            dynamic_dropdown = request.POST.getlist('dynamic_dropdown[]')  # Gets list of ids
            dynamic_quantity = request.POST.getlist('dynamic_quantity[]')
            courierOption = CourierOption.objects.get(id=request.POST.get('courier'))
            tracking = request.POST.get('tracking')
            noOfBoxes = int(request.POST.get('noOfBoxes'))
            boxFee = request.POST.get('boxFee')
            boxFee = 0 if boxFee == '' else boxFee
            print(dynamic_quantity)
            print(dynamic_dropdown)

            changes = []
            stocks = []

            static_product = Product.objects.get(id=static_dropdown)
            static_stock = Stock.objects.filter(product=static_product, active=1).order_by('inDate')
            if len(static_stock) < static_quantity:
                message = _('Error: Not enough stock for %(product)s') % {'product':static_product.productId}
                display_error(request, message)
                return redirect('home')
            for i in range(0,static_quantity):
                static_stock[i].active = False
                static_stock[i].outDate = todayDate()
                static_stock[i].save()
                stocks.append(static_stock[i])
            changes.append(StockChange(category='O', quantity=static_quantity, date=todayDate(),\
                                                      agent=request.user, product=static_product))
            if dynamic_dropdown != []:
                for i in range(0,len(dynamic_dropdown)):
                    dynamic_product = Product.objects.get(id=dynamic_dropdown[i])
                    dynamic_stock = Stock.objects.filter(product=dynamic_product, active=1).order_by('inDate')
                    if len(dynamic_stock) < int(dynamic_quantity[i]):
                        message = _('Error: Not enough stock for %(product)s') % {'product':dynamic_product.productId}
                        display_error(request, message)
                        return redirect('home')
                    for j in range(0, int(dynamic_quantity[i])):
                        dynamic_stock[j].active = False
                        dynamic_stock[j].outDate = todayDate()
                        dynamic_stock[j].save()
                        stocks.append(dynamic_stock[j])
                    changes.append(StockChange(category='O', quantity=static_quantity, date=todayDate(),\
                                                      agent=request.user, product=static_product))

            StockChange.objects.bulk_create(changes)
            stockDispatch = StockDispatch.objects.create(noOfBoxes=noOfBoxes,price=boxFee,tracking=tracking,\
                                               date=todayDate(),agent=request.user,courierOption=courierOption)
            dispatches = []
            for i in stocks:
                dispatches.append(DispatchItems(stockDispatch=stockDispatch, stock=i))
            DispatchItems.objects.bulk_create(dispatches)

            display_success(request, 'Success: Stock Dispatched')
            return redirect('home')
        
        else:
            cartons = request.POST.getlist('cartons')
            quantity = len(cartons)
            id = request.POST.get('id')
            product = Product.objects.get(id=id)
            courierOption = request.POST.get('courier')
            courierOption = CourierOption.objects.get(id=courierOption)
            tracking = request.POST.get('tracking')
            boxFee = request.POST.get('boxFee')
            boxFee = 0 if boxFee == '' else boxFee

            StockChange.objects.create(category='O', quantity=quantity, date=todayDate(),
                                        agent=request.user, product=product)
            stockDispatch = StockDispatch.objects.create(noOfBoxes=quantity,price=boxFee,tracking=tracking,\
                                                            date=todayDate(),agent=request.user,courierOption=courierOption)

            dispatchItems = []
            for id in cartons:
                carton = Stock.objects.get(id=int(id))
                carton.active = False
                carton.outDate = todayDate()
                carton.save()
                dispatchItems.append(DispatchItems(stockDispatch=stockDispatch, stock=carton))

            DispatchItems.objects.bulk_create(dispatchItems)

            display_success(request, 'Success: Stock Dispatched')
            return redirect('home')
               

## Returns details to view all changes on a product
@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewIndvChangesStock(request):

    id = request.GET['id']

    product = Product.objects.get(id=id)

    changes = StockChange.objects.filter(product=product).order_by("-date","-id")

    return render(request, 'StockManager/viewIndvChangesStock.html', {'changes':changes})


## Returns details of Dispatches of a product
@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewChangesStock(request):

    changes = StockChange.objects.order_by('-date','-id')
    
    for change in changes:
        if change.category == 'O':
            change.quantity = 0 - change.quantity

    return render(request, 'StockManager/viewChanges.html', {'changes':changes})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewDispatches(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        draw = int(request.GET.get('draw', 0))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')

        query = StockDispatch.objects.all().order_by('-date', '-id')
        if search_value:
            query = query.filter(Q(productId__icontains=search_value) |
                                Q(company__companyName__icontains=search_value))
        total_records = query.count()

        # Apply pagination
        paginator = Paginator(query, length)
        page_number = start // length + 1
        products_page = paginator.get_page(page_number)

        dispatchesData = []
        for dispatch in products_page:
            dispatchItems = DispatchItems.objects.filter(stockDispatch=dispatch)
            productCounts = {}
            for item in dispatchItems:
                productId = item.stock.product
                company = item.stock.product.company

                if productId in productCounts:
                    productCounts[productId]['count'] += 1
                else:
                    productCounts[productId] = {'count':1,'company':company}

            dispatchInfo = {
                'dateSent':dispatch.date,
                'tracking':dispatch.tracking,
                'agent':dispatch.agent.username,
                'courierOption':dispatch.courierOption.courier.name,
                'products':[{'product': productId.productId, 'company': details['company'].companyName, 'quantity': details['count']} for productId, details in productCounts.items()],
            }
            print(dispatchInfo)
            dispatchesData.append(dispatchInfo)

        return JsonResponse({
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': total_records,
                'data': dispatchesData,
            })
    
    else:
        return render(request, 'StockManager/viewDispatch.html', {})


@user_passes_test(is_worker, login_url='logIn')
def adjustStock(request):
    if request.method == 'POST':
        incOrDec = request.POST.get('incOrDec')
        quantity = int(request.POST.get('quantity'))
        product = Product.objects.get(id=request.POST.get('id'))
        stockList = Stock.objects.filter(product=product, active=1).order_by('-inDate','-id')
        stock = stockList[0]

        if incOrDec == 'increase':
            Stock_In_Function(request,product.productId,product.company,quantity,stock.inDate,product.stockType,\
                              product.sizeCbm,product.unitPrice,stock.notes,stock.location)
            StockChange.objects.create(category='I',quantity=quantity,date=stock.inDate,\
                                                     agent=request.user,product=stock.product)
            
        elif incOrDec == 'decrease':
            try:
                stock = stockList[quantity-1]
                for i in range(quantity):
                    stock = stockList[i]
                    stock.active = False
                    stock.outDate = todayDate()
                    stock.save()
                StockChange.objects.create(category='O', quantity=quantity, date=todayDate(),\
                                                          agent=request.user, product=product)
            except IndexError:
                return JsonResponse({'status': 'error', 'message': 'Error: Not enough stock.'})
        return JsonResponse({'status': 'success', 'message': 'Success: Stock Levels Updated'})

    else:
        display_error(request, 'Error: Unsupported request method. Please Try Again.')
        return redirect('home')
    

def changeLocation(request):
    if request.method == 'POST':
        location = request.POST['location']
        product = Product.objects.get(id=request.POST['id'])
        stockList = Stock.objects.filter(product=product)
        ogLocation = stockList[0].location

        for stock in stockList:
            stock.location = location
            stock.save()

        message = _('Success: The location for %(product)s has been changed from %(oglocation)s to %(location)s') % {'product':product.productId,'oglocation':ogLocation,'location':location}
        display_success(request, message)

        return redirect('home')
    

def uploadStock(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['csv_file']
            with codecs.getreader('utf-8')(file) as csvfile:
                csv_reader = csv.reader(csvfile)

                next(csv_reader, None)

                noCompany = []

                for row in csv_reader:
                    productId = row[0]
                    company = row[1].upper().strip()
                    stocktype = row[2]
                    size = row[3]
                    quantity = int(row[4])
                    date = row[5]
                    notes = row[6]
                    location = row[7]

                    unit_cbm = __cbm_dict__[stocktype][size]
                    unit_price = __price_dict__[stocktype][size]

                    try:
                        company = Company.objects.get(companyName=company)
                        Stock_In_Function(request,productId,company,\
                                          quantity,date,stocktype,unit_cbm,unit_price,notes,location)
                    except ObjectDoesNotExist:
                        noCompany.append(company)

                if noCompany != []:
                    message = _('Error: The following companies do not exist: %(noCompany)s') % {
                        'noCompany':', '.join(noCompany)
                    }
                    display_error(request, message)
                else:
                    display_success(request, 'Success: Stock Levels Updated')

                return redirect('home')

    else:
        form = CSVUploadForm()

    return render(request, 'StockManager/upload.html', {'form':form})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def optimise(request):
    scratch.main(5,5,3,20,np.random.randint(1, 4, 500).tolist())
    display_success(request, 'Success: Stock Optimised')
    return redirect('home')