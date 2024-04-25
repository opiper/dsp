from django import forms
from django.forms import ModelChoiceField
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from .models import Stock
from CompanyManager.models import Company
from warehouse.views import todayDate


class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.companyName


class AddStockForm(forms.ModelForm):
    productId = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Product ID'}),
        label='Product ID'
    )
    company = MyModelChoiceField(
        queryset=Company.objects.all().order_by('companyName'),
        to_field_name='companyName',
        required=True,
        blank=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Quantity','min':0}),
        label='Quantity'
    )
    sizeChoices = [
        ('SM', 'Small'),
        ('ME', 'Medium'),
        ('LA', 'Large')
    ]
    size = forms.ChoiceField(
        choices=sizeChoices,
        widget=forms.RadioSelect(attrs={'class':'form-check-input'}),
        label='Size'
    )
    stockChoices = [
        ('SK', 'SKU'),
        ('CA', 'Carton')
    ]
    stockType = forms.ChoiceField(
        choices=stockChoices,
        widget=forms.RadioSelect(attrs={'class':'form-check-input'}),
    )

    class Meta:
        model = Stock
        fields = ['productId','company','stockType','size','quantity','inDate','notes','location']
        widgets = {
            'inDate':forms.DateInput(attrs={'class':'form-control','value':todayDate(),'type':'date'}),
            'notes':forms.TextInput(attrs={'class':'form-control','placeholder':'Notes'}),
            'location':forms.TextInput(attrs={'class':'form-control','placeholder':'Location'}),
        }

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file')