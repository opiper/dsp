from datetime import datetime
from itertools import chain
from operator import attrgetter

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from ServiceManager.models import ServiceHistory, ServiceList
from StockManager.models import Product, Stock, StockChange
from CompanyManager.models import Company
from CourierManager.models import Courier

from .forms import CustomUserCreationForm, LogInForm


def is_worker(user):
    if user.role != 1:
        return True
    else:
        return False
        

def todayDate():
    return(datetime.today().strftime('%Y-%m-%d'))


# Utility function for displaying success messages
def display_success(request, message):
    messages.success(request, message)


# Utility function for displaying error messages
def display_error(request, message):
    messages.error(request, message)


## Basic Sign view to create a default User. Returns form if not requested as POST
def signUp(request):
    if request.method == 'POST':
        
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():

            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect('home')
        
    else:
        form = CustomUserCreationForm(request.POST)

    return render(request, 'warehouse/signUp.html', {'form':form})


## Basic Login View. Returns form if not requested by POST
def logIn(request):
    if request.method == 'POST':

        form = LogInForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user != None:
                login(request, user)
                return redirect('home')

            messages.error(request, 'Error: Invalid Credentials')

    else:
        form = LogInForm(request.POST)

    return render(request, 'warehouse/logIn.html', {'form':form})


## Logout View
def logOut(request):

    logout(request)

    return redirect('logIn')


## Grabs data required for the table displayed on the homepage
@login_required(login_url='logIn')
def home(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        draw = int(request.GET.get('draw', 0))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')

        if request.user.role == 1:
            productList = Product.objects.filter(company=request.user.company)
            results = []

            for product in productList:
                stocks = Stock.objects.filter(product=product)
                location = stocks[0]
                location = location.location
                
                quantity = 0
                for stock in stocks:
                    quantity += stock.quantity
                dict = {'productId':product.productId,'quantity':quantity,'stockType':stock.stockType,\
                        'company':product.company.companyName,'location':location,'id':product.id}
                results.append(dict)

            return render(request, 'warehouse/Company/companyHome.html', {'results':results,'user':request.user})

        elif request.user.role in [2, 3, 4]:
            query = Product.objects.filter(active=True).order_by("productId")
            if search_value:
                query = query.filter(Q(productId__icontains=search_value) |
                                     Q(company__companyName__icontains=search_value))
            total_records = query.count()

            # Apply pagination
            paginator = Paginator(query, length)
            page_number = start // length + 1
            products_page = paginator.get_page(page_number)

            results = []
            for product in products_page:
                stocks = Stock.objects.filter(product=product,active=1)
                locations = list(set(stock.location for stock in stocks)) if stocks.exists() else []
                quantity = len(stocks) if stocks.exists() else 0
                if quantity != 0:
                    quantity = str(quantity) + '/' + stocks[0].stockId[:stocks[0].stockId.find('-')] if product.stockType == 'CA' else quantity

                results.append({
                    'productId': product.productId,
                    'quantity': quantity,
                    'stockType': product.stockType,
                    'company': product.company.companyName,
                    'location': locations,
                    'id': product.id,
                })

            return JsonResponse({
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': total_records,
                'data': results,
            })
        
        else:
            messages.error(request, "Error: Invalid User Account. Contact Support")
            logout(request)
            return redirect(logIn)
    
    else:
        return render(request, 'warehouse/home.html', {})
    


def viewDailyOperations(request):
    if request.method == 'GET':
        date = todayDate()
        serviceHistory = ServiceHistory.objects.filter(date=date)
        stockChange = StockChange.objects.filter(date=date)

        result_list = sorted(
            chain(serviceHistory, stockChange),
            key=attrgetter('date')
        )

        return render(request, 'warehouse/viewDailyOperations.html', {'results':result_list,'date':date})
    
    else:
        date = request.POST['date']
        serviceHistory = ServiceHistory.objects.filter(date=date)
        stockChange = StockChange.objects.filter(date=date)

        result_list = sorted(
            chain(serviceHistory, stockChange),
            key=attrgetter('date')
        )

        return render(request, 'warehouse/viewDailyOperations.html', {'results':result_list,'date':date})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='home')
def clearStock(request):
    Stock.objects.all().delete()
    Product.objects.all().delete()
    display_success(request, _('Stock Cleared'))
    return redirect('home')

@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='home')
def clearCompanies(request):
    Company.objects.all().delete()
    display_success(request, _('Companies Cleared'))
    return redirect('home')

@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='home')
def clearCouriers(request):
    Courier.objects.all().delete()
    display_success(request, _('Couriers Cleared'))
    return redirect('home')

@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='home')
def clearServices(request):
    ServiceList.objects.all().delete()
    display_success(request, _('Services Cleared'))
    return redirect('home')