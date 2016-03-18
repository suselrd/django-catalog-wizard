# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from .models import OperationType


class FilterForm(forms.Form):
    operation_type = forms.ModelChoiceField(OperationType.objects, required=False)
    budget_min = forms.DecimalField(min_value=0, required=False)
    budget_max = forms.DecimalField(min_value=0, required=False)
    name = forms.CharField(max_length=50, required=False)
    name_contains = forms.CharField(max_length=50, required=False)
    keyword = forms.CharField(max_length=50, required=False)
    liked_by = forms.ModelMultipleChoiceField(User.objects, required=False)
    liked_by_target = forms.ModelChoiceField(User.objects, required=False)
    liked_by_from = forms.CharField(max_length=255, required=False)
    liked_by_to = forms.CharField(max_length=255, required=False)

    order_by = forms.ChoiceField(
        choices=[
            ('none', 'Ninguno'),
            ('price_asc', 'Menor Precio'),
            ('price_desc', 'Mayor Precio'),
            ('status_asc', 'Publicos Primero'),
            ('complex_order', 'Menor Precio, Publicos Primero')
        ],
        required=False
    )
