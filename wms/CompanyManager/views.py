import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from StockManager.models import Product, Stock
from warehouse.models import CustomUser
from warehouse.views import is_worker

from .forms import CompanyAddForm
from .models import Company


## Returns list of customers to be displayed to the user
@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewCompany(request):

    companyList = Company.objects.all()

    return render(request, 'CompanyManager/viewCompany.html', {'results' : companyList})

## Add a new customer. Bare bones atm. Returns form if method isn't POST
@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def addCompany(request):
    if request.method == 'POST':

        form = CompanyAddForm(request.POST, request.FILES)

        if form.is_valid():

            companyName = form.cleaned_data['companyName'].upper().replace(" ", "")

            if Company.objects.filter(companyName=companyName).exists():

                messages.error(request, 'Error: Company Already Exists')

                return redirect('viewCompany')
            
            form.save()

            company = Company.objects.get(companyName=companyName)
            directorName = form.cleaned_data['directorName']
            if directorName != None:
                username = companyName + '_' + directorName
            else:
                username = companyName
            password = password = str(secrets.token_urlsafe(5))
            user = CustomUser.objects.create_user(username=username,password=password,role=1,company=company)
            user.save()

            message = _('Success: Company Created Successfully. Password = %(password)s, username = %(username)s') % {'password':password, 'username':username}
            messages.success(request, message)

            return redirect('viewCompany')
        
        
    else:
        
        form = CompanyAddForm(request.POST, request.FILES)

    return render(request, 'CompanyManager/addCompany.html', {'form': form})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def editCompany(request):
    pass


## Delete customer. No checks currently
@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def deleteCompany(request):
    if request.method == 'POST':

        companyId = request.POST['companyId']

        Company.objects.filter(id=companyId).delete()

        messages.success(request, 'Success: Customer deleted successfully!')

        return redirect('viewCompany')
    

@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewIndvCompany(request):
    if request.method == 'POST':
        companyId = request.POST['customerId']

        company = Company.objects.get(id=companyId)

        return render(request, 'CompanyManager/viewIndvCompany.html', {'company':company})
    

@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewCompanyStock(request):
    id = request.GET['id']
    company = Company.objects.get(id=id)
    products = Product.objects.filter(active=True,company=company).order_by("productId")
    results = []
    for product in products:
        stocks = Stock.objects.filter(product=product)
        if stocks.exists():
                location = stocks[0].location
        else:
            location = ''
        
        quantity = 0
        if stocks[0].stockType == 'CA':
            for stock in stocks:
                quantity += 1
        else:
            for stock in stocks:
                quantity += stock.quantity
        dict = {'productId':product.productId,'quantity':quantity,'stockType':stock.stockType,\
                'company':product.company.companyName,'id':product.id}
        results.append(dict)

    return render(request, 'CompanyManager/viewCompanyStock.html', {'results':results})