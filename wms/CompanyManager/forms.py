from django import forms
from .models import Company


class CompanyAddForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['companyName','companyCode','companyAddress','directorName','email',\
        'weChat','phoneNumber','vatNumber','businessLicence']
        widgets = {
            'companyName':forms.TextInput(attrs={'class':'form-control','placeholder':'Name'}),
            'companyCode':forms.TextInput(attrs={'class':'form-control','placeholder':'Company Code'}),
            'companyAddress':forms.TextInput(attrs={'class':'form-control','placeholder':'Company Address'}),
            'directorName':forms.TextInput(attrs={'class':'form-control','placeholder':"Director's Name"}),
            'email':forms.EmailInput(attrs={'class':'form-control','placeholder':'Company Email'}),
            'weChat':forms.TextInput(attrs={'class':'form-control','placeholder':'Company WeChat'}),
            'phoneNumber':forms.NumberInput(attrs={'class':'form-control','placeholder':'Company Phone Number'}),
            'vatNumber':forms.TextInput(attrs={'class':'form-control','placeholder':'VAT Number'}),
            'businessLicence':forms.FileInput(attrs={'class':'form-control'}),
        }