import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from ..forms import RegisterForm
from ..models import Customer, Account, ReservationInfo


def register(request):
    '''
    Register a new user
    '''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("form valid")
            email = form.cleaned_data['email']
            email = email.lower().strip()
            # No duplciate email are allowed
            exist = Customer.objects.get(email=email)
            if exist:
                return HttpResponseRedirect(reverse('polls:index_warning', args=(2,)))
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            card1 = form.cleaned_data['card1']
            card2 = form.cleaned_data['card2']
            card3 = form.cleaned_data['card3']
            firstName = form.cleaned_data['firstName']
            lastName = form.cleaned_data['lastName']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zip']
            phone = form.cleaned_data['phone']
            # Save cutomer
            cus = Customer(
                first_name=firstName,
                last_name=lastName,
                password=password1,
                email=email,
                address=address,
                city=city,
                state=state,
                zip=zipcode,
                phone=phone,
            )
            cus.save()
            reservation_default = ReservationInfo.objects.get(
                reservation_id=-1)
            acc_id = 1
            # Save account with credit card
            account_1 = Account(
                customer=cus,
                account_id=acc_id,
                reservation=reservation_default,
                create_date=str(datetime.datetime.now().date()),
                credit_card=card1
            )
            account_1.save()
            acc_id = acc_id+1
            if card2:
                account_2 = Account(
                    customer=cus,
                    account_id=acc_id,
                    reservation=reservation_default,
                    create_date=str(datetime.datetime.now().date()),
                    credit_card=card2
                )
                account_2.save()
                acc_id = acc_id+1
            if card3:
                account_3 = Account(
                    customer=cus,
                    account_id=acc_id,
                    reservation=reservation_default,
                    create_date=str(datetime.datetime.now().date()),
                    credit_card=card3
                )
                account_3.save()
            # Create user in Django authentication syste,
            user = User.objects.create_user(email, email, password1)
            user.first_name = firstName
            user.last_name = lastName
            user.save()
            # Login new register user
            login(request, user)
            print("correct")
        else:
            print("error: "+form.errors.as_json())
            form = RegisterForm()
    return HttpResponseRedirect(reverse('polls:index_default'))


def validate_register_email(request):
    email = request.POST.get('email', None)
    data = {
        'is_taken': Customer.objects.filter(email=email).exists(),
    }
    return JsonResponse(data)
