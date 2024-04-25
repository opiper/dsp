from django import forms
from .models import CourierOption

class AddCourierOptionForm(forms.ModelForm):
    finalPrice = forms.FloatField(
        widget=forms.NumberInput(attrs={'class':'form-control'}),
        label='Final  Price'
    )
    class Meta:
        model = CourierOption
        fields = ['box','price','dropship','envelope','finalPrice']
        widgets = {
            'box':forms.RadioSelect(attrs={'class':'form-check-input'}),
            'price':forms.RadioSelect(attrs={'class':'form-check-input'}),
            'dropship':forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'evelope':forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
