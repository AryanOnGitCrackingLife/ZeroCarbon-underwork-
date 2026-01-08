from django import forms
from .models import FoodConsumption, ElectricityUsage, Travel, WasteSegregation


class FoodForm(forms.ModelForm):
    class Meta:
        model = FoodConsumption
        fields = ["food", "quantity_kg"]



class ElectricityForm(forms.ModelForm):
    class Meta:
        model = ElectricityUsage
        fields = ['units_kwh']


class TravelForm(forms.ModelForm):
    class Meta:
        model = Travel
        fields = ['mode', 'distance_km']


class WasteForm(forms.ModelForm):
    class Meta:
        model = WasteSegregation
        fields = ['quantity_kg']
