from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from django.http import HttpResponse
from .models import *
from .forms import *
from rest_framework import viewsets
from .serializers import *
# django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import generics


# Create your views here.
def index(request):
    #get the request in
    # do some logic with models from
    # return some webpage to the user
    products = Product.objects.all()  # A list of all of the products.
    return render(request, 'index.html', {'products': products})

def product_individual(request, prodid):
    # Get the product with id - prodid
    product = Product.objects.get(id=prodid)
    return render(request, 'product_individual.html', {'product': product})

class UserSignupView(CreateView):
    model = APIUser
    form_class = UserSignupForm
    template_name  = 'user_signup.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')

class UserLoginView(LoginView):
    template_name= 'login.html'

def logout_user(request):
    logout(request)
    return redirect("/")

@login_required
def add_to_basket(request, prodid):
    user = request.user
    # is there a shopping basket for the user 
    basket = Basket.objects.filter(user_id= user.id, is_active=True).first()
    if not basket:
        # create a new one
        Basket.objects.create(user_id = user)
        basket = Basket.objects.filter(user_id=user, is_active=True).first()
    
    # get the product
    product = Product.objects.get(id=prodid)
    sbi = BasketItem.objects.filter(basket_id=basket, product_id=product).first()
    if sbi is None:
        # there is no basket item for that product 
        # create one
        sbi = BasketItem(basket_id=basket, product_id = product)
        sbi.save() 
    else:
        # basket item already exists
        # just add one to the quantity
        sbi.quantity = sbi.quantity + 1
        sbi.save()
    return render(request, 'product_individual.html', {'product': product, 'added':True})

@login_required
def show_basket(request):
    # get the user object
    # does a shopping basket exist? -> your basket is empty
    # load all shopping basket items
    # display on page
    user = request.user
    basket = Basket.objects.filter(user_id=user, is_active=True).first()
    if basket is None:
        # to do: show basket empty.
        return render(request, 'basket.html', {'empty':True})
    else:
        # load all the basket items
        sbi = BasketItem.objects.filter(basket_id=basket)
        # is this list empty?
        if sbi.exists():
            # normal flow
            return render(request, 'basket.html', {'basket':basket, 'sbi':sbi})
        else:
            # to do: show basket empty
            return render(request, 'basket.html', {'empty':True})

@login_required
def remove_item(request, sbi):
    basketitem = BasketItem.objects.get(id=sbi)
    if basketitem is None:
        return redirect("/basket")  # if error redirect to shopping basket
    else:
        if basketitem.quantity > 1:
            basketitem.quantity = basketitem.quantity - 1
            basketitem.save()  # save our changes to the database
        else:
            basketitem.delete()  # delete the basket item
    return redirect("/basket")

@login_required
def order(request):
    # load in all data we need, user, basket, items
    user = request.user
    basket = Basket.objects.filter(user_id=user, is_active=True).first()
    if basket is None:
        return redirect("/")
    sbi = BasketItem.objects.filter(basket_id=basket)
    if not sbi.exists():  # if there are no items
        return redirect("/")

    # POST or GET?
    if request.method == "POST":
        # check if form is valid
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user_id = user
            order.basket_id = basket
            total = 0.0
            for item in sbi:
                total += float(item.price())
            order.total_price = total
            order.save()
            basket.is_active = False
            basket.save()
            return render(request, 'ordercomplete.html', {'order':order, 'basket':basket, 'sbi':sbi})

        else:
            return render(request, 'orderform.html', {'form':form, 'basket':basket, 'sbi':sbi})
    else:
        # show the form
        form = OrderForm()
        return render(request, 'orderform.html', {'form':form, 'basket':basket, 'sbi':sbi})

@login_required
def previous_orders(request):
    user = request.user
    orders = Order.objects.filter(user_id=user)
    return render(request, 'previous_orders.html', {'orders':orders})


# def howdy():
# return JsonResponse({'status' : 'OK'})

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class BasketViewSet(viewsets.ModelViewSet):
    serializer_class = BasketSerializer
    queryset = Basket.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user # get the current user
        if user.is_superuser:
            return Basket.objects.all() # return all the baskets if a superuser requests
        else:
            # For normal users, only return the current active basket
            shopping_basket = Basket.objects.filter(user_id=user, is_active=True)
            return shopping_basket

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user # get the current user
        if user.is_superuser:
            return Order.objects.all() # return all the baskets if a superuser requests
        else:
            # For normal users, only return the current active basket
            orders = Order.objects.filter(user_id=user)
            return orders

class APIUserViewSet(viewsets.ModelViewSet):
    queryset = APIUser.objects.all()
    serializer_class = APIUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']
        passsword = validated_data['password'] # Extract the username, email and passwor from the serializer
        new_user = APIUser.objects.create_user(username=username, email=email, password=passsword) # Create a new APIUser
        new_user.save() # Save the new user
        return new_user

class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny] #No login is needed to access this route
    queryset = queryset = APIUser.objects.all()

class AddBasketItemAPIView(generics.CreateAPIView):
    serializer_class = AddBasketItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = BasketItem.objects.all()

class RemoveBasketItemAPIView(generics.CreateAPIView):
    serializer_class = RemoveBasketItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = BasketItem.objects.all()

class CheckoutAPIView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()