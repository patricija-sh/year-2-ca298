# from multiprocessing import AuthenticationError
# from tkinter import Widget
from cProfile import label
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.forms import ModelForm, ModelChoiceField
from .models import APIUser, Order
from django.db import transaction

class UserSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):  # this is the meta data for the form
        model = APIUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)  # start saving but dont save to the database just yet
        user.is_admin = False
        user.save()
        return user

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Your password'}))

class OrderForm(ModelForm):
    shipping_addr = forms.CharField(label="Shipping address", widget=forms.TextInput(attrs={'placeholder': 'Shipping Address'}))

    class Meta:
        model=Order
        fields = ['shipping_addr']