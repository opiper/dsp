from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from warehouse.views import is_worker

from .forms import AddCourierOptionForm
from .models import Courier, CourierOption


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewCourier(request):
    courierList = Courier.objects.all()

    return render(request, 'CourierManager/viewCourier.html', {'couriers':courierList})


@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def addCourier(request):
    if request.method == 'POST':
        name = request.POST['courierName']

        if not Courier.objects.filter(name=name).exists():
            courier = Courier.objects.create(name=name)
            courier.save()

        else:
            messages.error(request, 'Error: That courier already exists')
            return redirect(viewCourier)

        messages.success(request, 'Success: Courier Successfully added')
        return redirect(viewCourier)

    else:
        return render(request, 'CourierManager/addCourier.html')
    

@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def viewCourierOption(request):
    if request.method == 'POST':
        courierId = request.POST['courierId']
        courier = Courier.objects.get(id=courierId)
        courierOptionsList = CourierOption.objects.filter(courier=courier)
        return render(request, 'CourierManager/viewCourierOption.html',{'courierId':courierId,'courierOptions':courierOptionsList})



@login_required(login_url='logIn')
@user_passes_test(is_worker, login_url='logIn')
def addCourierOption(request):
    if request.method == 'POST':
        form = AddCourierOptionForm(request.POST)
        if form.is_valid():
            courierId = request.POST['courierId']
            courier = Courier.objects.get(id=courierId)
            obj = form.save(commit=False)
            obj.courier = courier
            obj.save()

            messages.success(request, 'Success: Courier option added')
            return redirect('viewCourier')
    else:
        courierId = request.GET['id']
        form = AddCourierOptionForm(request.POST)

    return render(request, 'CourierManager/addCourierOption.html', {'form':form,'courierId':courierId})