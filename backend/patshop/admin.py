from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import APIUser
from .models import *

# Register your models here.
# The reason for this is it makes it easier to debug later on.
admin.site.register(APIUser, UserAdmin)
admin.site.register(Product)
admin.site.register(Basket)
admin.site.register(BasketItem)
admin.site.register(Order)